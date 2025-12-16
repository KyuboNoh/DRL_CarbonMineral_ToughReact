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

# 2. Write INCON (Free Format)
with open(OUTPUT_FILE, 'w', newline='\n') as f:
    # No Header "INCON". Start straight away.
    
    for i, label in enumerate(labels):
        # Depth Calc
        depth = max_z - z_vals[i]
        if depth < 0: depth = 0
        
        # Physics
        p = P_SURFACE + (RHO_W * 9.81 * depth)
        t = T_SURFACE + (GRAD_T * depth)
        
        # --- LINE 1: Element Name ---
        # TOUGH2 reads A5. We ensure it is 5 chars long.
        # If label is 'A11 0', it is 5 chars.
        # We wrap in quotes just in case, but standard text is safer:
        f.write(f"{label:<5}\n")
        
        # --- LINE 2: Variables (Free Format) ---
        # We just separate by spaces. TOUGH V4 handles this well.
        # Vars: P, Salt, CO2, T
        # Use high precision to be safe.
        f.write(f" {p:.5E}  {SALINITY:.5E}  0.00000E+00  {t:.5E}\n")

    # Optional: Write a terminator line (some versions like it)
    f.write("\n")

print(f"Done! '{OUTPUT_FILE}' created.")