import pandas as pd
import re

def clean_gymnastics_data():
    input_file = "gymnastics_history.csv"
    output_file = "cleaned_gymnastics.csv"
    
    print("🧹 Starting data cleaning...")
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    all_data = []
    current_gymnast = "Unknown"
    
    # Define standard headers we want in the final file
    # We map the "messy" index to the "clean" column name
    # Index 0=Date, 6=VT, 7=UB, 8=BB, 9=FX, 10=AA
    
    for line in lines:
        row = line.strip().split(',')
        
        # Skip empty lines or junk "Meet Scores" lines
        if not row or not row[0] or "Meet Scores" in row[0]:
            continue
            
        # DETECT HEADER ROW: If it starts with "Date", it's a new section
        if row[0] == "Date":
            # The last column usually holds the name (e.g., "Annabelle_MMS")
            raw_name = row[-1]
            if "_MMS" in raw_name:
                current_gymnast = raw_name.replace("_MMS", "").strip()
            print(f"   Found section for: {current_gymnast}")
            continue # Skip the actual header line, we just wanted the name
            
        # PROCESS DATA ROW
        # Ensure row has enough columns (Ansel might have more events)
        if len(row) < 10: 
            continue
            
        # Extract basic info
        date = row[0]
        meet = row[1]
        level = row[4]
        
        # Helper function to split "9.700 1" -> 9.7
        def get_score(val):
            if not val: return 0.0
            # Take the first part of the string (the score)
            try:
                # Remove quotes if present
                clean_val = val.replace('"', '').split(' ')[0]
                return float(clean_val)
            except:
                return 0.0

        # Create a clean record
        # Note: We are assuming the column order based on your snippet
        # Girls: VT(6), UB(7), BB(8), FX(9), AA(10)
        # Boys: This might differ, but let's try to map dynamically if possible
        
        record = {
            'Date': date,
            'Gymnast': current_gymnast,
            'Level': level,
            'Meet': meet,
            'VT': get_score(row[6]),  # Vault
            'AA': get_score(row[10])  # All Around
        }

        # Handle Gender Differences (Boys have 6 events, Girls 4)
        # We check the Gymnast name to decide how to parse
        if current_gymnast == "Ansel":
            # Boys order in MSO is usually: FX, PH, SR, VT, PB, HB
            # We need to map row indices carefully. 
            # If your Ansel CSV section follows standard MSO export:
            # 6=FX, 7=PH, 8=SR, 9=VT, 10=PB, 11=HB, 12=AA (Adjust as needed)
            # For now, let's just save what we can. 
            # simpler approach: Just save the girls' columns for now to fix the crash
            pass 
        else:
            # Girls Standard
            record['UB'] = get_score(row[7])
            record['BB'] = get_score(row[8])
            record['FX'] = get_score(row[9])
        
        # ADD MEN'S DATA IF AVAILABLE (Ansel)
        # If the row has extra columns, it might be Ansel
        # For this specific "Fix", let's focus on the girls first or use a generic "Event X" approach
        # But to match your snippet:
        if current_gymnast == "Ansel":
             # Assuming Ansel's columns align similarly for now, or we skip specific events
             # to prevent index errors. 
             # Let's try to grab his specific events if they exist
             try:
                 record['FX'] = get_score(row[6]) # Floor is usually first for men
                 record['PH'] = get_score(row[7])
                 record['SR'] = get_score(row[8])
                 record['VT'] = get_score(row[9])
                 record['PB'] = get_score(row[10])
                 record['HB'] = get_score(row[11])
                 record['AA'] = get_score(row[12]) 
             except:
                 pass # Fallback

        all_data.append(record)

    # Save to new CSV
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    print(f"✅ Created {output_file} with {len(df)} rows.")
    print(df.head())

if __name__ == "__main__":
    clean_gymnastics_data()
