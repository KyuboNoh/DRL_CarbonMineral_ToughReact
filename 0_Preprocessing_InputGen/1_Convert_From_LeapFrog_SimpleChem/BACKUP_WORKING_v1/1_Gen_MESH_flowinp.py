import os
import sys

"""
===============================================================================
TOUGHREACT INPUT GENERATOR (Exact User Specification)
===============================================================================

WARNING: THIS SCRIPT GENERATES INPUTS WITH KNOWN RISK FACTORS
The output 'flow.inp' strictly follows the user-provided template. 
Please be aware of the following potential issues in this format:

1. PARAM BLOCK:
   - DELTEN = -1.0: This forces Manual Time Stepping (Table Lookup). 
     It requires the extra line " 1." (DLT) immediately following.
     If the simulation exceeds the provided table, it may struggle to 
     auto-step effectively compared to DELTEN > 0.
   - KDATA = 10: This increases printout frequency significantly (printing 
     at every Newton iteration if improperly combined with other flags).
   - MOP(16) = 6: This is a very strict doubling criterion (convergence in 
     <6 iterations). Standard is 4. This may slow down the run.

2. GENER BLOCK:
   - "COM3h": This text is placed in columns 31-40. Standard TOUGH2 expects 
     a FLOAT (Enthalpy) here. "COM3h" may cause "Input Conversion Errors" 
     depending on the specific compiler/version of TOUGHREACT.
   - Merged Name ("i 4INJ01"): The Element name and Source name are 
     running together. This risks the simulator searching for a non-existent 
     block named "i 4I" instead of "i 4".
   - Wrapped Table Data: The time/rate data is formatted with 3 floats per 
     line. Standard TOUGH input expects specific Time/Rate pairs. 
     This format relies on the Fortran reader handling wrapped lines, 
     which is often unstable.

===============================================================================
"""

# =============================================================================
# --- USER CONFIGURATION ---
# =============================================================================

INPUT_DIR   = "INPUT"
OUTPUT_DIR  = "OUTPUT"
SOURCE_FILE = "example_model.dat"

# --- INJECTION SETTINGS ---
# Note: These values populate the specific fields in the user's template
INJ_X     = 319000.0  
INJ_Y     = 5100900.0 
INJ_Z     = 1000.0    
INJ_RATE  = 1.0       
INJ_ENTHALPY_STR = ".538E+05" # Kept as string to match format exactly

# =============================================================================
# --- INTERNAL LOGIC ---
# =============================================================================

INPUT_PATH  = os.path.join(INPUT_DIR, SOURCE_FILE)
FLOW_OUT    = os.path.join(OUTPUT_DIR, "flow.inp")
MESH_OUT    = os.path.join(OUTPUT_DIR, "MESH") # Generated just for context
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_blocks(filename):
    if not os.path.exists(filename):
        print(f"Warning: Input file {filename} not found. Using default logic."); return {}
    with open(filename, 'r') as f: lines = f.readlines()
    blocks = {}; current = None; buffer = []
    keywords = ["ROCKS", "PARAM", "ELEME", "CONNE", "GENER", "INCON", "SOLVR", "MULTI", "SELEC", "START", "ENDCY"]
    for line in lines:
        s = line.strip()
        if not s: continue
        is_key = False
        for k in keywords:
            if s.startswith(k):
                if current: blocks[current] = buffer
                current = k; buffer = []; is_key = True; break
        if not is_key and current: buffer.append(line)
    if current: blocks[current] = buffer
    return blocks

print(f"--- Processing {INPUT_PATH} ---")
data = parse_blocks(INPUT_PATH)

# ==========================================
# 0. FIND INJECTOR
# ==========================================
injector_elem = " i 4 " # Default fallback from your snippet
min_dist_sq = 1.0e20

if 'ELEME' in data:
    for line in data['ELEME']:
        if len(line) < 80: continue
        try:
            name = line[0:5] 
            x, y, z = float(line[50:60]), float(line[60:70]), float(line[70:80])
            dist_sq = (x - INJ_X)**2 + (y - INJ_Y)**2 + (z - INJ_Z)**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                injector_elem = name
        except ValueError: continue

if injector_elem != " i 4 ":
    print(f" -> FOUND: Nearest element is '{injector_elem}'. Using this name.")

# ==========================================
# 1. GENERATE FLOW.INP (EXACT FORMAT)
# ==========================================
print(f"Generating {FLOW_OUT}...")
with open(FLOW_OUT, 'w', newline='\n') as f:
    f.write("TOUGHREACT 3D: Fixed GENER Alignment\n")
    
    # ROCKS
    if 'ROCKS' in data:
        f.write("ROCKS----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
        for line in data['ROCKS']: f.write(line)
        f.write("\n")

    # MULTI
    f.write("MULTI----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("    3    3    3    6\n") 

    f.write("SELEC....2....3....4....5....6....7....8....9...10...11...12...13...14...15...16\n")
    f.write("    1                                      0    0    0    0    0    0    1\n")
    f.write("       0.8       0.8\n")

    f.write("SOLVR----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("5  Z1  O0    8.0e-1     1.0e-7\n")

    f.write("START----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("REACT----1MOPR(20)-2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("00021004\n")
    f.write("----*----1 MOP: 123456789*123456789*1234 ---*----5----*----6----*----7----*----8\n")
    
    # --- PARAM BLOCK (EXACT USER REQUEST) ---
    f.write("PARAM----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    
    # Line 1: KDATA=10, MCYC=9999, MOP(16)=6 (The problematic settings requested)
    f.write("     20 10               9999          0          000000000012000060120500\n")
    
    # Line 2: DELTEN = -1.0
    f.write(" 0.000E+00 3.156E+09       -1.0 1.000E+05                  9.81 \n")
    
    # Line 3: The Manual DLT Step (Required when DELTEN is negative)
    f.write(" 1.\n")
    
    # Line 4 & 5
    f.write(" 1.E-4     1.E00\n")
    f.write("             200.e5               .06               1.e-12               75.\n")
    
    # TIMES
    f.write("TIMES----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("2\n")
    f.write(" 3.156E+06 3.156E+07\n")

    # GENER (EXACT USER FORMAT)
    f.write("GENER----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    
    # Formatting the merged header: " i 4INJ01" 
    # {injector_elem.strip()} ensures we don't have too many spaces if the name is short
    # We construct it to look exactly like the snippet provided.
    elem_str = injector_elem.rstrip() # " i 4"
    if len(elem_str) < 5: elem_str = f"{elem_str:<4}" # Ensure at least length 4 for look
    
    # Line 1: Header with "COM3h"
    f.write(f" {elem_str}INJ01                   3     COM3h            {INJ_ENTHALPY_STR}        \n")
    
    # Line 2: 3 floats (Time, Rate, Time)
    # 0.0, 1.0, 3.15569E6
    f.write("    0.0000E+00   1.0000E+00    3.15569E6\n")
    
    # Line 3: 3 floats (Rate, Time, Rate)
    # 1.0, 3.15569E6, 0.0
    f.write("    1.0000E+00   3.15569E6     0.0000E+00\n")
    
    # Line 4: 2 floats (Time, Rate)
    # 3.15569E6, 0.0
    f.write("    3.15569E6    0.0000E+00\n")

    f.write("\n")
    f.write("ENDCY\n")

print(f"Done. Exact 'flow.inp' created in '{OUTPUT_DIR}'.")