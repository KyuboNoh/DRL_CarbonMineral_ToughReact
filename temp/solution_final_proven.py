import os

OUTPUT_FILE = "flow.inp" # Directly write to flow.inp
# --- USER CONFIGURATION ---
ROCK_NAME = "Backg"
DENSITY   = 2600.0
POROSITY  = 0.10
PERM      = 1.0e-13
COND      = 2.51
SP_HEAT   = 920.0
INJ_BLOCK = "A3M65"
INJ_RATE  = 1.0

# --- HELPER: STRICT 10-CHAR FORMATTER ---
def fmt_10char(val):
    if val == -1.0:
        return "       -1."
    if val == 0.0:
        return "        0."
        
    # Use 4 decimals (Standard)
    s = f"{val:.4E}"
    # Force compression ONLY if > 10 chars (e.g. -1.2345E+10)
    # logic from Step 552 which passed
    if len(s) > 10:
        s = s.replace("E+0", "E0").replace("E+", "E")
    return f"{s:>10}"

print(f"--- Generating {OUTPUT_FILE} with Proven 'Unit 3' Success Logic ---")

with open(OUTPUT_FILE, 'w', newline='\n') as f:
    f.write("TOUGHREACT 3D: Final Protected Version\n")

    # 1. ROCKS BLOCK
    f.write("ROCKS----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    # Using 10.0f for Density (as this worked in Step 742 compared to 10.2f)
    line1 = f"{ROCK_NAME:<5}    0{DENSITY:10.0f}.{POROSITY:10.4f}" \
            f"{PERM:10.3E}{PERM:10.3E}{1.0e-14:10.3E}{COND:10.3f}{SP_HEAT:10.0f}."
    f.write(line1 + "\n")
    f.write(" 1.00E-09                            0.0\n")
    f.write("    3           0.30       0.05\n")
    f.write("    3           0.00       0.00      1.000E+05      1.00E+07\n")
    f.write("\n") # Blank line to safety terminate ROCKS

    # 2. MULTI
    f.write("MULTI----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("    3    3    3    6\n")

    # 3. SELEC
    f.write("SELEC....2....3....4....5....6....7....8....9...10...11...12...13...14...15...16\n")
    f.write("    1                                      0    0    0    0    0    0    1\n")
    f.write("       0.8       0.8\n")

    # 4. SOLVR
    f.write("SOLVR----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("5  Z1   O0    8.0e-1     1.0e-7\n")

    # 5. START
    f.write("START----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")

    # 6. REACT
    f.write("REACT----1MOPR(20)-2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("00021004\n")
    f.write("----*----1 MOP: 123456789*123456789*1234 ---*----5----*----6----*----7----*----8\n")

    # 7. PARAM (CRITICAL FIX)
    f.write("PARAM----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    
    # Line 1: NOITE(8), KDATA(8), MCYC(4), MOPs
    noite, kdata, mcyc = 8, 50, 2000
    line_param1 = f"{noite:>8}{kdata:>8}{mcyc:>4} 00000010  4   0500" 
    f.write(line_param1 + "\n")
    
    # Line 2: Timings (Strict 10-char format)
    t_max  = 3.1558e8
    delten = -1.0
    t_step = 1.0e-5
    
    # Construct strictly: Blank(10) + TMAX(10) + DELTEN(10) + TSTEP(10) + Gravity stuff
    # Using fmt_10char which returns padded string
    s_tmax = fmt_10char(t_max)
    s_delten = fmt_10char(delten)
    s_tstep = fmt_10char(t_step)
    
    line_param2 = f"          {s_tmax}{s_delten}{s_tstep}"
    line_param2 += "A1 50 0.01      9.81" # Gravity appended safely
    f.write(line_param2 + "\n")
    
    # PARAM Lines 3-4 (Defaults)
    f.write(" 1.\n")
    f.write(" 1.E-4     1.E00\n")
    f.write("             200.e5               .06               1.e-12               75.\n")
    
    # 8. TIMES
    f.write("TIMES----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    f.write("    2\n")
    f.write(f"{fmt_10char(1.5779e8)}{fmt_10char(3.1558e8)}\n")

    # 9. GENER
    f.write("GENER----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    # Name(5) Block(5) Comp(5) LTAB(5) Rate(10)
    line_gen = f"INJ01{INJ_BLOCK:<5}COM3       {fmt_10char(INJ_RATE)}"
    f.write(line_gen + "\n")
    f.write("\n") # Blank line to terminate GENER [cite: 1]

    # 10. ENDCY
    f.write("ENDCY\n")

print("Done.")
