import os

OUTPUT_FILE = "solute.inp"

# --- USER CONFIGURATION ---
NUM_COMPONENTS = 11   # NWCOM: Primary chemical components
NUM_MINERALS   = 17   # NWMIN: Minerals
NUM_AQUEOUS    = 32   # NWAQ:  Secondary aqueous species to output

# Output File Names
DB_FILE      = "TherAkin10.dat"
ITER_FILE    = "iter.out"
CONC_FILE    = "co2d_conc.tec"
MIN_FILE     = "co2d_min.tec"
GAS_FILE     = "co2d_gas.tec"
TIME_FILE    = "co2d_tim.out"

print(f"--- Generating {OUTPUT_FILE} with Corrected Lists ---")

with open(OUTPUT_FILE, 'w', newline='\n') as f:
    f.write("# Title\n")
    f.write("'TOUGHREACT 3D CO2 Injection'\n")

    f.write("#ISPIA,itersfa,ISOLVC,NGAMM,NGAS1,ichdump,kcpl,Ico2h2o,nu\n")
    f.write(f"    2    0       5      1    1        0      1       0    0\n")

    f.write("#constraints for chemical solver:  sl1min, rcour, stimax, cnfact\n")
    f.write(f"   1.00e-5   0.000     6.0     1.0\n")

    f.write("#Read input and output file names:\n")
    f.write(f"{DB_FILE:<30} ! thermodynamic database\n")
    f.write(f"{ITER_FILE:<30} ! iteration information\n")
    f.write(f"{CONC_FILE:<30} ! aqueous concentrations in tecplot form\n")
    f.write(f"{MIN_FILE:<30} ! mineral data  in tecplot form\n")
    f.write(f"{GAS_FILE:<30} ! gas data  in tecplot form\n")
    f.write(f"{TIME_FILE:<30} ! concentrations at specific elements over time\n")

    f.write("#Weighting parameters\n")
    f.write(f"       1.0       1.0   1.0d-09   1.1d-05           ! itime wupc,dffun,dffung\n")

    f.write("#data to convergence criteria:\n")
    f.write(f"    1 0.100E-03  200 0.100E-05 0.100E-07  0.00E-05  0.00E-05    !  ........ TOLDC,TOLDR \n")

    # --- OUTPUT CONTROL (The Source of the Error) ---
    f.write("#NWTI NWNOD NWCOM NWMIN NWAQ NWADS NWEXC iconflag minflag  igasflag\n")
    # We specify we want to output 32 aqueous species (NWAQ=32)
    f.write(f"   100    0   {NUM_COMPONENTS}   {NUM_MINERALS}   {NUM_AQUEOUS}    0      0        0      1          1\n")

    f.write("#pointer of nodes for writing in time:\n")
    f.write("\n")

    # --- COMPONENT LIST ---
    f.write("#pointer of components for writing:\n")
    # Generates "1  2  3  ... 11"
    comps = "  ".join(str(i) for i in range(1, NUM_COMPONENTS + 1))
    f.write(f"   {comps}\n")

    # --- MINERAL LIST ---
    f.write("#pointer of minerals for writing:\n")
    # Generates "1  2  3  ... 17"
    mins = "  ".join(str(i) for i in range(1, NUM_MINERALS + 1))
    f.write(f"   {mins}\n")

    # --- AQUEOUS SPECIES LIST (The Fix) ---
    f.write("#Individual aqueous species for which to output concentrations:\n")
    # THE FIX: We generate indices 1 to 32 to match the count NWAQ=32
    # This prevents the "last input record starts with 32" error.
    aq_species = "  ".join(str(i) for i in range(1, NUM_AQUEOUS + 1))
    f.write(f"   {aq_species}\n")

    f.write("#Adsorption species for which to output concentrations in time and plot files:\n")
    f.write("\n")
    f.write("#Exchange species for which to output concentrations in time and plot files:\n")
    f.write("\n")

    f.write("#IZIWDF IZBWDF IZMIDF IZGSDF IZADDF IZEXDF IZPPDF IZKDDF IZBGDF (default types of chemical zones)\n")
    f.write(f"    1    1    1    1    0    0    1    0    0  \n")

    f.write("#ELEM(a5) NSEQ NADD IZIW IZBW IZMI IZGS IZAD IZEX izpp IZKD IZBG\n")
    f.write("\n")

    f.write("# this \"end\" record is needed now\n")
    f.write("end \n")

print("Done. 'solute.inp' generated with correct lists.")