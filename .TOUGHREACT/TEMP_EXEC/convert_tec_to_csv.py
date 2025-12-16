import os
import re
import csv

def convert_to_paraview_csv():
    target_file = "co2d_conc.tec"
    
    if not os.path.exists(target_file):
        print(f"Error: {target_file} not found. Make sure the simulation ran.")
        return

    print(f"Processing {target_file} for ParaView...")
    
    with open(target_file, 'r') as fin:
        lines = fin.readlines()

    # Storage for processed data
    headers = []
    all_rows = []
    current_time = 0.0

    # Regex patterns
    # Finds text inside quotes: "X(m)" -> X(m)
    var_pattern = re.compile(r'"(.*?)"')
    # Finds time in Zone line: Zone T= "4.00 sec"
    zone_pattern = re.compile(r'Zone\s+T=\s*"(.*?)\s*sec"', re.IGNORECASE)

    for line in lines:
        line = line.strip()
        if not line: continue

        # 1. Parse Header
        if line.lower().startswith('variables'):
            # Extract quoted names
            matches = var_pattern.findall(line)
            if matches:
                headers = ["Time"] + matches # Add Time column at start
            continue

        # 2. Parse Time Zone
        if line.lower().startswith('zone'):
            # Extract time string (e.g. 4.000E+00)
            match = zone_pattern.search(line)
            if match:
                try:
                    current_time = float(match.group(1))
                except ValueError:
                    current_time = 0.0
            continue

        # 3. Parse Data Rows
        # If line starts with number, it's data
        if line[0].isdigit() or line[0] == '-' or line[0] == '+':
            try:
                # Split whitespace
                values = line.split()
                # Prepend the current time
                row = [current_time] + values
                all_rows.append(row)
            except:
                continue

    # Write to CSV
    output_csv = "co2d_conc_paraview.csv"
    with open(output_csv, 'w', newline='') as fout:
        writer = csv.writer(fout)
        if headers:
            writer.writerow(headers)
        writer.writerows(all_rows)

    print(f"Success! Created {output_csv} with {len(all_rows)} rows.")

if __name__ == "__main__":
    convert_to_paraview_csv()