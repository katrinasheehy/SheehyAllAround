import pandas as pd
import os
import re

# Configuration
FOLDER = "ansel_history"
SOURCE_FILE = "Ansel_Mas Watanabe_session.html"
FULL_PATH = os.path.join(FOLDER, SOURCE_FILE)
OUTPUT_CSV = "ansel_mas_watanabe_raw.csv"

def split_score_rank(val):
    """Splits '9.300 1T' into ('9.300', '1T')"""
    val = str(val).strip()
    if not val or val.lower() == "nan":
        return "0.0", ""
    # Matches the score (decimal) and everything following it (rank)
    match = re.search(r"(\d+\.\d+)\s*(.*)", val)
    if match:
        return match.group(1), match.group(2)
    return val, ""

def main():
    if not os.path.exists(FULL_PATH):
        print(f"❌ File {FULL_PATH} not found.")
        return

    # 1. Load the data table
    all_tables = pd.read_html(FULL_PATH)
    target_df = None
    for df in all_tables:
        cols = [str(c).lower() for c in df.columns]
        if 'aa' in cols and any('floor' in c or 'vault' in c for c in cols):
            target_df = df
            break

    if target_df is None:
        print("❌ Individual results table not found in HTML.")
        return

    # 2. Initialize the exact Master Headers (26 columns)
    master_headers = [
        "Date", "Gymnast", "Meet", "Session", "Level", "Division", 
        "Meet_Rank", "Meet_Rank_Total", "VT", "VT_Rank", "UB", "UB_Rank", 
        "BB", "BB_Rank", "FX", "FX_Rank", "PH", "PH_Rank", "SR", "SR_Rank", 
        "PB", "PB_Rank", "HB", "HB_Rank", "AA", "AA_Rank"
    ]
    
    final_rows = []

    # 3. Process each athlete row
    for _, row in target_df.iterrows():
        # Map raw columns to our standardized score/rank logic
        # Note: MSO Column indices: Floor(2), Pommel(3), Rings(4), Vault(5), PBars(6), HiBar(7), AA(8)
        # We use column name lookups for safety
        def get_val(keyword):
            col = next((c for c in target_df.columns if keyword.lower() in str(c).lower()), None)
            return split_score_rank(row[col]) if col else ("0.0", "")

        fx_s, fx_r = get_val('Floor')
        ph_s, ph_r = get_val('Pommel')
        sr_s, sr_r = get_val('Rings')
        vt_s, vt_r = get_val('Vault')
        pb_s, pb_r = get_val('PBars')
        hb_s, hb_r = get_val('HiBar')
        aa_s, aa_r = get_val('AA')

        # Create the dictionary matching the 26 headers exactly
        data_row = {
            "Date": "2026-02-13",
            "Gymnast": row[target_df.columns[0]], # Athlete Name
            "Meet": "2026 Mas Watanabe",
            "Session": "4",
            "Level": "4D1",
            "Division": row[target_df.columns[4]] if len(target_df.columns) > 4 else "",
            "Meet_Rank": aa_r,
            "Meet_Rank_Total": "152",
            "VT": vt_s, "VT_Rank": vt_r,
            "UB": "0.0", "UB_Rank": "", # Girls event
            "BB": "0.0", "BB_Rank": "", # Girls event
            "FX": fx_s, "FX_Rank": fx_r,
            "PH": ph_s, "PH_Rank": ph_r,
            "SR": sr_s, "SR_Rank": sr_r,
            "PB": pb_s, "PB_Rank": pb_r,
            "HB": hb_s, "HB_Rank": hb_r,
            "AA": aa_s, "AA_Rank": aa_r
        }
        final_rows.append(data_row)

    # 4. Save to CSV
    output_df = pd.DataFrame(final_rows, columns=master_headers)
    output_df.to_csv(OUTPUT_CSV, index=False)
    
    print(f"✅ Success! Created {OUTPUT_CSV} with {len(output_df)} rows.")
    print(f"🎯 Target count: 152. Found: {len(output_df)}.")

if __name__ == "__main__":
    main()
