import numpy as np
import toughio
import sys

# --- CONFIGURATION ---
MESH_FILE = "MESH"
OUTPUT_FILE = "INCON"

# EOS14 Initial Conditions (4 Primary Variables)
# 1. Pressure (Pa)
# 2. Salinity (Mass Fraction)
# 3. CO2 Mass Fraction (or Gas Saturation + 10)
# 4. Temperature (C)

P_SURFACE = 1.013e5   
T_SURFACE = 15.0      
GRAD_T    = 0.03      
RHO_W     = 1000.0    
SALINITY  = 0.1       

print(f"--- Generating Free-Format {OUTPUT_FILE} ---")

# 1. Read Mesh
try:
    mesh_data = toughio.read_mesh(MESH_FILE)
    if hasattr(mesh_data, 'centers'):
        labels, centers = mesh_data.labels, mesh_data.centers
    else:
        eleme = mesh_data.get('elements', mesh_data.get('ELEME'))
        labels = np.array(list(eleme.keys()))
        centers = np.array([v['center'] for v in eleme.values()])
except Exception as e:
    print(f"Error reading MESH: {e}")
    sys.exit(1)

z_vals = centers[:, 2]
max_z = np.max(z_vals)

# 2. Write INCON (Fixed Format)
with open(OUTPUT_FILE, 'w', newline='\n') as f:
    # Header is REQUIRED for TOUGHREACT to identify the section/file
    f.write("INCON----1----*----2----*----3----*----4----*----5----*----6----*----7----*----8\n")
    
    for i, label in enumerate(labels):
        # Depth Calc
        depth = max_z - z_vals[i]
        if depth < 0: depth = 0
        
        # Physics
        p = P_SURFACE + (RHO_W * 9.81 * depth)
        t = T_SURFACE + (GRAD_T * depth)
        
        # --- LINE 1: Element Name + Sequence Number ---
        # Format: Name(A5), NSEQ(I5). Using NSEQ=0 ensures parsed correctly.
        f.write(f"{label:<5}    0\n")
        
        # --- LINE 2: Variables (Fixed Width) ---
        # Using 20.14E for safety and precision.
        # Order: Pressure, Salinity, CO2 (0.0), Temperature
        f.write(f"{p:20.14E}{SALINITY:20.14E} 0.0000000000000E+00{t:20.14E}\n")

    # Terminator
    f.write("\n")

print(f"Done! '{OUTPUT_FILE}' created.")