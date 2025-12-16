import sys

MESH_FILE = "MESH"

print(f"--- Scanning {MESH_FILE} for Rock Types ---")

try:
    with open(MESH_FILE, 'r', errors='ignore') as f:
        found_eleme = False
        materials = set()
        count = 0
        
        for line in f:
            # TOUGH MESH structure: 
            # Block 'ELEME' starts the element list.
            # Block 'CONNE' ends it.
            if line.strip().startswith('ELEME'):
                found_eleme = True
                continue
            
            if found_eleme:
                # Stop if we hit the connections or empty line
                if line.strip() == '' or line.strip().startswith('CONNE') or line.strip().startswith('+++'):
                    break
                
                # In standard TOUGH fixed format:
                # Cols 1-5: Element Name
                # Cols 16-20: Rock Type (Material Name)
                # Python string slicing is 0-indexed, so we look at index 15 to 20
                if len(line) >= 20:
                    mat_name = line[15:20] 
                    materials.add(f"'{mat_name}'") # Keep quotes to see spaces
                    count += 1
                    
    print(f"Scanned {count} elements.")
    print("Unique Rock Types found in MESH:")
    for m in materials:
        print(f"  -> {m}")
        
    print("\nACTION: Update your 'flow.inp' ROCKS block to match this name EXACTLY.")

except Exception as e:
    print(f"Error reading file: {e}")