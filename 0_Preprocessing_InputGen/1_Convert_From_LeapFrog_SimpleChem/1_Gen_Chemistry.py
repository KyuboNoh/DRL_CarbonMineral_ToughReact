import os

# =============================================================================
# TOUGHREACT CHEMICAL INPUT GENERATOR (Asterisk Format - WORKING BASELINE)
# =============================================================================
# Purpose:
#     Generates chemical.inp strictly following the provided "Working Example" format.
#     
#     Format Rules:
#     1. Headers: Must start with '#' (e.g., # PRIMARY AQUEOUS SPECIES).
#     2. Terminators: Use '*' instead of 'end' for data blocks.
#     3. Spacing: Strict columns.
#     4. Missing Blocks: If NO data (e.g., Minerals), use '*' immediately.
#     5. Zones: Include Initial Water/Mineral Zones, even if simple.
# =============================================================================

OUTPUT_FILE = "OUTPUT/chemical.inp"
os.makedirs("OUTPUT", exist_ok=True)

# CHEMISTRY CONFIGURATION
PRIMARY_SPECIES = [
    "h2o", "h+", "na+", "k+", "ca+2", "mg+2", 
    "hco3-", "so4-2", "cl-", "sio2(aq)", "alo2-", "fe+2", "o2(aq)"
]

# EMPTY MINERALS LIST (Known Working State)
MINERALS = []

GASES = ["co2(g)"]

print(f"--- Generating {OUTPUT_FILE} (Asterisk Format - NO MINERALS) ---")

with open(OUTPUT_FILE, 'w', newline='\n') as f:
    # --- TITLE ---
    f.write("# Title\nDeep Sky Thetford: Asterisk Format\n")
    f.write("#" + "-"*77 + "\n")
    f.write("# DEFINITION OF THE GEOCHEMICAL SYSTEM\n")
    
    # --- PRIMARY SPECIES ---
    f.write("# PRIMARY AQUEOUS SPECIES\n")
    for species in PRIMARY_SPECIES:
        # Format: Name(20 chars) + Flag(5 chars)
        f.write(f"{species:<20}{0:>5}\n")
    f.write("*\n")

    # --- AQUEOUS KINETICS ---
    f.write("# AQUEOUS KINETICS\n")
    # Empty for now (use *)
    f.write("*\n")

    # --- AQUEOUS COMPLEXES ---
    f.write("# AQUEOUS COMPLEXES\n")
    # Empty (use *)
    f.write("*\n")

    # --- MINERALS ---
    f.write("# MINERALS\n")
    # Empty list -> Just write terminator
    f.write("*\n")

    # --- GASES ---
    f.write("# GASES\n")
    for gas in GASES:
        f.write(f"{gas:<20}{0:>5}\n")
    f.write("*\n")
    
    # --- SURFACE COMPLEXES ---
    f.write("# SURFACE COMPLEXES\n")
    f.write("*\n")

    # --- SPECIES DECAY ---
    f.write("# species with Kd and decay    decay constant(1/s)\n")
    f.write("*\n")

    # --- EXCHANGEABLE CATIONS ---
    f.write("# EXCHANGEABLE CATIONS\n")
    f.write("*\n")
    
    f.write("#" + "-"*77 + "\n")

    # ==========================================================
    # INITIAL AND BOUNDARY WATER ZONES (Required by format)
    # ==========================================================
    f.write("# INITIAL AND BOUNDARY WATER TYPES\n")
    # niwtype=1, nbwtype=0 (1 Zone defined)
    f.write("1   0\n") 
    
    # Zone 1 Header
    f.write("# Index  Speciation T(C)  P(bar)\n")
    f.write("1          15.0            1.013\n") 
    f.write("#         icon        guess         ctot\n")
    
    # Write entries for ALL primary species
    # Format matches working example: Name(10) Icon(I8) Guess(E15.3) Total(E15.3) * 0.
    
    for species in PRIMARY_SPECIES:
        conc = 1.0e-10
        if species == 'h2o': conc = 1.0
        if species == 'h+':  conc = 1.0e-7 
        if species == 'na+': conc = 0.1 
        if species == 'cl-': conc = 0.1
        
        # Name (left align 10)
        str_name = f"{species:<10}" 
        # Icon (right align 9) -> "        1"
        str_icon = f"{1:>9}"
        # Guess (15.3E) -> "      1.000e-10"
        str_guess = f"{conc:15.3E}"
        str_tot   = f"{conc:15.3E}"
        
        f.write(f"{str_name}{str_icon}{str_guess}{str_tot}   *  0.\n")
        
    f.write("*\n")

    # ==========================================================
    # INITIAL MINERAL ZONES
    # ==========================================================
    f.write("# INITIAL MINERAL ZONES\n")
    # 1 Zone
    f.write("1\n") # Num Zones
    f.write("1\n") # Zone Index
    
    # No Minerals -> No lines here.
    # Just terminator? 
    # The working example had minerals sections even if empty?
    # Actually, if we declare 1 zone, we might need entries OR just * if list is empty.
    # Logic: writes NOTHING inside the zone if list is empty.
    
    f.write("*\n")

    # --- REMAINING ZONES ---
    f.write("# INITIAL gas ZONES\n*\n")
    f.write("# Permeability-Porosity Zones\n*\n")
    f.write("# INITIAL SURFACE ADSORPTION ZONES\n*\n")
    f.write("# INITIAL LINEAR EQUILIBRIUM Kd ZONE\n*\n")
    f.write("# INITIAL ZONES OF CATION EXCHANGE\n*\n")
    
    f.write("# end\n")

print("Done. Chemical.inp updated to Asterisk Format (NO MINERALS).")