import pandas as pd
import cloudscraper
import os
from io import StringIO
from meet_mapping import MMS_MEET_IDS

# Files
INPUT_CSV = "cleaned_gymnastics.csv"
OUTPUT_CSV = "session_raw_data.csv"

def get_mms_url(meet_id, session_id):
    return f"https://www.mymeetscores.com/meet.pl?meetid={meet_id}&session={session_id}"

def scrape_full_table(url, meet_name, session_id, expected_count):
    scraper = cloudscraper.create_scraper()
    print(f"📡 Harvesting Session: {meet_name} (Sess {session_id})")
    
    try:
        resp = scraper.get(url)
        # Use StringIO to avoid the future warning in pandas
        tables = pd.read_html(StringIO(resp.text))
        
        for df in tables:
            # Identify the results table by checking for Vault/V columns
            if any(col in df.columns for col in ['Vault', 'V', 'Bars', 'UB']):
                # Standardize headers to our unified format
                rename_map = {
                    'Gymnast': 'Athlete', 'Vault': 'VT', 'Bars': 'UB', 
                    'Beam': 'BB', 'Floor': 'FX', 'AA': 'AA'
                }
                df.rename(columns=rename_map, inplace=True)
                
                # Add Context Metadata
                df['Meet'] = meet_name
                df['Session'] = session_id
                
                # --- VALIDATION CHECKPOINT ---
                found = len(df)
                if int(found) != int(expected_count):
                    print(f"   ⚠️ Validation Alert: Found {found} athletes, but CSV says {expected_count}.")
                else:
                    print(f"   ✅ Validation Pass: Collected all {found} athletes.")
                
                return df
    except Exception as e:
        print(f"   ❌ Error reaching MMS: {e}")
    return None

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌ Error: {INPUT_CSV} not found.")
        return

    # 1. Find 2026 Girls Meets from your CSV
    df_history = pd.read_csv(INPUT_CSV)
    girls_2026 = df_history[
        (df_history['Date'].str.startswith('2026')) & 
        (df_history['Gymnast'].isin(['Annabelle', 'Azalea']))
    ].copy()

    all_raw_data = []

    # 2. Loop through and harvest
    for _, row in girls_2026.iterrows():
        meet = row['Meet']
        if meet in MMS_MEET_IDS and MMS_MEET_IDS[meet]:
            url = get_mms_url(MMS_MEET_IDS[meet], row['Session'])
            df_session = scrape_full_table(url, meet, row['Session'], row['Meet_Rank_Total'])
            
            if df_session is not None:
                all_raw_data.append(df_session)
        else:
            print(f"⏩ Skipping {meet}: No MMS ID yet (use manual HTML scoop if needed).")

    # 3. Save the Raw Session Data
    if all_raw_data:
        final_df = pd.concat(all_raw_data, ignore_index=True)
        
        # Clean numeric columns (remove ranks/text from scores)
        score_cols = ['VT', 'UB', 'BB', 'FX', 'AA']
        for col in score_cols:
            if col in final_df.columns:
                final_df[col] = final_df[col].astype(str).str.split(' ').str[0]
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce')

        final_df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n🎉 Raw data harvest complete! {len(final_df)} rows saved to {OUTPUT_CSV}")
    else:
        print("\n❌ No data collected. Check your MMS IDs or internet connection.")

if __name__ == "__main__":
    main()
