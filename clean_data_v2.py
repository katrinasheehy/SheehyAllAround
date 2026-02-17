import pandas as pd
import re

def clean_and_restore():
    input_file = "gymnastics_history.csv"
    output_file = "cleaned_gymnastics.csv" # Overwriting the simple one
    
    print("🧹 Restoring detailed data (Ranks, Sessions, Divisions)...")
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    all_data = []
    current_gymnast = "Unknown"
    
    for line in lines:
        row = line.strip().split(',')
        
        # Skip empty/junk lines
        if not row or not row[0] or "Meet Scores" in row[0]: continue
            
        # Detect Header / New Gymnast Section
        if row[0] == "Date":
            if "_MMS" in row[-1]:
                current_gymnast = row[-1].replace("_MMS", "").strip()
            continue 
            
        if len(row) < 10: continue

        # Helper to split "9.700 1" into (9.7, 1)
        def parse_cell(val):
            if not val: return 0.0, ""
            val = val.replace('"', '').strip()
            parts = val.split(' ')
            try:
                score = float(parts[0])
                rank = parts[1] if len(parts) > 1 else ""
                # remove "T" from rank (e.g. 1T -> 1) for sorting if desired, 
                # but let's keep it for display
                return score, rank
            except:
                return 0.0, ""

        # Extract Core Data
        date = row[0]
        meet = row[1]
        session = row[3] # Preserving Session
        level = row[4]
        division = row[5] # Preserving Division
        
        # Parse Scores and Ranks (Girls Standard)
        vt_score, vt_rank = parse_cell(row[6])
        ub_score, ub_rank = parse_cell(row[7])
        bb_score, bb_rank = parse_cell(row[8])
        fx_score, fx_rank = parse_cell(row[9])
        aa_score, aa_rank = parse_cell(row[10])

        record = {
            'Date': date, 'Gymnast': current_gymnast, 
            'Meet': meet, 'Session': session, 'Level': level, 'Division': division,
            'VT': vt_score, 'VT_Rank': vt_rank,
            'UB': ub_score, 'UB_Rank': ub_rank,
            'BB': bb_score, 'BB_Rank': bb_rank,
            'FX': fx_score, 'FX_Rank': fx_rank,
            'AA': aa_score, 'AA_Rank': aa_rank,
            # Placeholders for Men's events (so Ansel fits in later)
            'PH': 0.0, 'PH_Rank': '', 'SR': 0.0, 'SR_Rank': '', 
            'PB': 0.0, 'PB_Rank': '', 'HB': 0.0, 'HB_Rank': ''
        }
        all_data.append(record)

    df = pd.DataFrame(all_data)
    # Ensure columns are ordered nicely
    cols = ['Date', 'Gymnast', 'Meet', 'Session', 'Level', 'Division', 
            'VT', 'VT_Rank', 'UB', 'UB_Rank', 'BB', 'BB_Rank', 'FX', 'FX_Rank', 
            'PH', 'PH_Rank', 'SR', 'SR_Rank', 'PB', 'PB_Rank', 'HB', 'HB_Rank',
            'AA', 'AA_Rank']
    df = df[cols]
    
    df.to_csv(output_file, index=False)
    print(f"✅ Success! {output_file} created with {len(df)} rows and full details.")

if __name__ == "__main__":
    clean_and_restore()
