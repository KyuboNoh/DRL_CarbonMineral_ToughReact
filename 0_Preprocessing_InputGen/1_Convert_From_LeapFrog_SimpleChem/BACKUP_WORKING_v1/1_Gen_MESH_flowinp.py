import os
import sys
import math

"""
===============================================================================
TOUGHREACT INPUT CONVERTER (v22: Working GENER + Flexible Timing)
===============================================================================
- GENER Block: EXACT MATCH (Character-for-character) to your working snippet.
- Time Stepping: Now uses your requested logic:
    - 0 to 10 Years: Output every 2 Years.
    - 10 to 100 Years: Output every 20 Years.
===============================================================================
"""

# =============================================================================
# --- CONFIGURATION (EDIT HERE) ---
# =============================================================================

INPUT_DIR   = "INPUT"
OUTPUT_DIR  = "OUTPUT"
SOURCE_FILE = "example_model.dat"

# --- TIMING CONFIGURATION (IN YEARS) ---
INJ_DURATION_YRS = 10.0    # Inject for 10 Years
MONITOR_END_YRS  = 100.0   # Continue simulation until 100 Years

# Output Frequency (How often to write to disk)
OUTPUT_FREQ_INJ  = 2.0     # Every 2 years during injection
OUTPUT_FREQ_MON  = 20.0    # Every 20 years after injection

# --- PHYSICS CONSTANTS ---
SEC_PER_YEAR = 3.15576e7  # Standard Julian year seconds
P_SURFACE = 1.013e5   
T_SURFACE = 15.0      
GRAD_T    = 0.03      
RHO_W     = 1000.0    
SALINITY  = 0.1       

# --- INJECTION PARAMETERS ---
INJ_X     = 319000.0  
INJ_Y     = 5100900.0 
INJ_Z     = 1000.0    
INJ_RATE  = 5.0       

# --- CHEMISTRY CONFIG ---
NUM_COMPS    = 13
NUM_MINERALS = 4
NUM_AQUEOUS  = 13

# =============================================================================
# --- INTERNAL LOGIC ---
# =============================================================================

INPUT_PATH  = os.path.join(INPUT_DIR, SOURCE_FILE)
MESH_OUT    = os.path.join(OUTPUT_DIR, "MESH")
FLOW_OUT    = os.path.join(OUTPUT_DIR, "flow.inp")
INCON_OUT   = os.path.join(OUTPUT_DIR, "INCON")
SOLUTE_OUT  = os.path.join(OUTPUT_DIR, "solute.inp")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_time_schedule(inj_dur, end_time, step_inj, step_mon):
    """
    Generates a list of output times in seconds based on yearly inputs.
    """
    times = []
    current_t = 0.0
    
    # Phase 1: Injection (0 to 10 years)
    while current_t < inj_dur - 1e-5: # Float tolerance
        current_t += step_inj
        if current_t > inj_dur: current_t = inj_dur
        times.append(current_t * SEC_PER_YEAR)
        
    # Phase 2: Monitoring (10 to 100 years)
    while current_t < end_time - 1e-5:
        current_t += step_mon
        if current_t > end_time: current_t = end_time
        times.append(current_t * SEC_PER_YEAR)
        
    # Remove duplicates and ensure strictly increasing
    return sorted(list(set(times)))

def fmt_10char(val_str):
    try:
        val = float(val_str)
        if val == -1.0: return "       -1."
        if val == 0.0:  return "        0."
        s = f"{val:.3E}"
        if len(s) > 10: s = s.replace("E+0", "E").replace("E+", "E")
        return f"{s:>10}"
    except ValueError:
        return f"{val_str:>10}"

def parse_blocks(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Input file not found: {filename}")
    with open(filename, 'r') as f:
        lines = f.readlines()
    blocks = {}
    current_block = None
    buffer = []
    keywords = ["ROCKS", "PARAM", "ELEME", "CONNE", "GENER", "INCON", "SOLVR", "MULTI", "SELEC", "START", "ENDCY"]
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        is_keyword = False
        for k in keywords:
            if stripped.startswith(k):
                if current_block: blocks[current_block] = buffer
                current_block = k
                buffer = []
                is_keyword = True
                break
        if not is_keyword and current_block:
            buffer.append(line)
    if current_block: blocks[current_block] = buffer
    return blocks

print(f"--- Processing {INPUT_PATH} ---")
try:
    data = parse_blocks(INPUT_PATH)
except FileNotFoundError as e:
    print(f"Error: {e}"); sys.exit(1)

# ==========================================
# 0. FIND INJECTOR
# ==========================================
elements = []
z_values = [] 
min_dist_sq = 1.0e20
injector_elem = None

if 'ELEME' in data:
    for line in data['ELEME']:
        if len(line) < 80: continue
        try:
            name = line[0:5] 
            x = float(line[50:60])
            y = float(line[60:70])
            z = float(line[70:80])
            elements.append(name)
            z_values.append(z)
            dist_sq = (x - INJ_X)**2 + (y - INJ_Y)**2 + (z - INJ_Z)**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                injector_elem = name
        except ValueError: continue

if injector_elem:
    print(f" -> FOUND: Injector assigned to '{injector_elem}'")

# ==========================================
# 1. GENERATE MESH
# ==========================================
print(f"Generating {MESH_OUT}...")
with open(MESH_OUT, 'w', newline='\n') as f:
    if 'ELEME' in data:
        f.write("ELEME----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
        for line in data['ELEME']: f.write(line)
        f.write("\n")
    if 'CONNE' in data:
        f.write("CONNE----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
        for line in data['CONNE']: f.write(line)
        f.write("\n")

# ==========================================
# 2. GENERATE FLOW.INP
# ==========================================
print(f"Generating {FLOW_OUT}...")
with open(FLOW_OUT, 'w', newline='\n') as f:
    f.write("TOUGHREACT 3D: Exact GENER Format + Flexible Times\n")
    
    # ROCKS
    if 'ROCKS' in data:
        f.write("ROCKS----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
        for line in data['ROCKS']:
            if len(line) < 10: continue
            try:
                name = line[0:5].strip()
                den = float(line[10:20].strip())
                por = float(line[20:30].strip())
                p1 = float(line[30:40].strip())
                p2 = float(line[40:50].strip())
                p3 = float(line[50:60].strip())
                cond = float(line[60:70].strip())
                cp = float(line[70:80].strip())
                f.write(f"{name:<5}{2:>5}{den:10.3f}{por:10.3f}{p1:10.2E}{p2:10.2E}{p3:10.2E}{cond:10.3f}{cp:10.3f}\n")
                f.write("  1.00E-09                           0.5\n")
                f.write("    7           .457       .30        1.       .05\n")
                f.write("    7           .457       .00    5.1e-5      1.e7      .999\n")
            except: f.write(line)
        f.write("\n")

    # MULTI
    f.write("MULTI----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("    3    3    3    6\n") 

    f.write("SELEC....2....3....4....5....6....7....8....9...10...11...12...13...14...15...16\n")
    if 'SELEC' in data:
        for line in data['SELEC']: f.write(line)
    else:
        f.write("    1                                      0    0    0    0    0    0    1\n")
        f.write("       0.8       0.8\n")

    f.write("SOLVR----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("5  Z1  O0    8.0e-1     1.0e-7\n")

    f.write("START----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("REACT----1MOPR(20)-2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("00021004\n")
    f.write("----*----1 MOP: 123456789*123456789*1234 ---*----5----*----6----*----7----*----8\n")
    
    # PARAM
    # Calc Max Time in Seconds for TSTOP
    t_max_sec = MONITOR_END_YRS * SEC_PER_YEAR
    
    f.write("PARAM----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write(f"{8:>8}{50:>8}{4000:>4} 00000010  4   0500\n")
    line2 = f"          {fmt_10char(t_max_sec)}{fmt_10char(-1.0)}{fmt_10char(1.0e-5)}A1 50 0.01      9.81"
    f.write(line2 + "\n")
    f.write(" 1.\n 1.E-4     1.E00\n             200.e5               .06               1.e-12               75.\n")
    
    # TIMES (Generated from Year Logic)
    time_list = generate_time_schedule(INJ_DURATION_YRS, MONITOR_END_YRS, OUTPUT_FREQ_INJ, OUTPUT_FREQ_MON)
    
    f.write("TIMES----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write(f"{len(time_list):>5}\n")
    for i, t in enumerate(time_list):
        f.write(fmt_10char(t))
        if (i + 1) % 8 == 0: f.write("\n")
    if len(time_list) % 8 != 0: f.write("\n")

    # GENER (EXACT MATCHING STRINGS from YOUR WORKING VERSION)
    f.write("GENER----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    if injector_elem:
        # 1. Header (Fixed String Structure)
        # "  i 4INJ01                   3     COM3h             .538E+05"
        # 5+5=10. +19=29. '3' at 30. +5=35. 'COM3h' at 36.
        # Enthalpy needs to look like ".538E+05"
        
        elem_s = f"{injector_elem:<5}"
        header = f"{elem_s}INJ01{' '*19}3{' '*5}COM3h{' '*13}.538E+05"
        f.write(header + "\n")
        
        # 2. Row 1: Times
        # "    0.0000E+00   3.15569E+08    3.15569E11"
        # EXACTLY 14 chars per column.
        t1 = "    0.0000E+00"
        t2 = "   3.15569E+08"
        t3 = "    3.15569E11"
        f.write(f"{t1}{t2}{t3}\n")
        
        # 3. Row 2: Rates
        # "           5.0    0.0000E+00    0.0000E+00"
        r1 = "           5.0"
        r2 = "    0.0000E+00"
        r3 = "    0.0000E+00"
        f.write(f"{r1}{r2}{r3}\n")
        
        # 4. Row 3: Enthalpies
        # "      .538E+05      .538E+05      .538E+05"
        h1 = "      .538E+05"
        f.write(f"{h1}{h1}{h1}\n")
        
    f.write("\n") # Blank Line
    f.write("ENDCY\n")

# ==========================================
# 3. GENERATE INCON
# ==========================================
print(f"Generating {INCON_OUT}...")
if z_values:
    max_z = max(z_values)
    with open(INCON_OUT, 'w', newline='\n') as f:
        f.write("INCON----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
        for i, name in enumerate(elements):
            depth = max(0, max_z - z_values[i])
            p = P_SURFACE + (RHO_W * 9.81 * depth)
            t = T_SURFACE + (GRAD_T * depth)
            f.write(f"{name:<5}    0\n")
            f.write(f"{p:20.14E}{SALINITY:20.14E} 0.0000000000000E+00{t:20.14E}\n")
        f.write("\n")

# ==========================================
# 4. GENERATE SOLUTE.INP
# ==========================================
print(f"Generating {SOLUTE_OUT}...")
with open(SOLUTE_OUT, 'w', newline='\n') as f:
    f.write("# Title\n'TOUGHREACT 3D CO2 Injection'\n")
    f.write("#ISPIA,itersfa,ISOLVC,NGAMM,NGAS1,ichdump,kcpl,Ico2h2o,nu\n")
    f.write(f"{2:>5}{0:>5}{5:>5}{1:>5}{1:>5}{0:>5}{1:>5}{0:>5}{0:>5}\n")
    f.write("#constraints for chemical solver\n   1.00e-5   0.000     6.0     1.0\n")
    f.write("#Read input and output file names:\n")
    f.write("TherAkin10.dat                 ! thermodynamic database\n")
    f.write("iter.out                       ! iteration information\n")
    f.write("co2d_conc.tec                  ! aqueous concentrations\n")
    f.write("co2d_min.tec                   ! mineral data\n")
    f.write("co2d_gas.tec                   ! gas data\n")
    f.write("co2d_tim.out                   ! time concentrations\n")
    f.write("#Weighting parameters\n       1.0       1.0   1.0d-09   1.1d-05\n")
    f.write("#data to convergence criteria:\n    1 0.100E-03  200 0.100E-05 0.100E-07  0.00E-05  0.00E-05\n")
    f.write(f"#NWTI NWNOD NWCOM NWMIN NWAQ NWADS NWEXC iconflag minflag  igasflag\n")
    f.write(f"{100:>5}{0:>5}{NUM_COMPS:>5}{NUM_MINERALS:>5}{NUM_AQUEOUS:>5}{0:>5}{0:>5}{0:>5}{1:>5}{1:>5}\n")
    f.write("#pointer of nodes for writing in time:\n\n")
    f.write("#pointer of components:\n")
    f.write("  ".join(str(i) for i in range(1, NUM_COMPS + 1)) + "\n")
    f.write("#pointer of minerals:\n")
    f.write("  ".join(str(i) for i in range(1, NUM_MINERALS + 1)) + "\n")
    f.write("#Individual aqueous species:\n")
    f.write("  ".join(str(i) for i in range(1, NUM_AQUEOUS + 1)) + "\n")
    f.write("#Adsorption species:\n\n#Exchange species:\n\n")
    f.write("#IZIWDF ... (default zones)\n    1    1    1    1    0    0    1    0    0\n")
    f.write("#ELEM(a5) ... (specific nodes)\n\n")
    f.write("# end record\nend\n")

print(f"Done. Files created in '{OUTPUT_DIR}'.")