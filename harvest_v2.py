import pandas as pd
import os
import re
import cloudscraper
from bs4 import BeautifulSoup
from io import StringIO
from meet_mapping import MMS_MEET_IDS

# Settings
INPUT_CSV = "cleaned_gymnastics.csv"
OUTPUT_CSV = "session_raw_data.csv"
HTML_FOLDER = "ansel_history"

def clean_score(val):
    """Strictly extracts only a decimal number (e.g., '9.200 1' -> 9.2)"""
    if pd.isna(val) or val == "": return 0.0
    match = re.search(r"(\d+\.\d+)", str(val))
    return float(match.group(1)) if match else 0.0

def parse_session_table(df, discipline, meet, session):
    """Standardizes a raw table based on if it's Men's or Women's."""
    df = df.copy()
    
    # Try to find the Athlete Name column (it varies by site)
    name_col = next((c for c in df.columns if any(x in str(c).lower() for x in ['gymnast', 'athlete', 'name'])), None)
    if name_col:
        df = df.rename(columns={name_col: 'Athlete'})
    
    # Standardize Event Headers
    if discipline == "Men":
        mapping = {'Floor': 'FX', 'Pommel': 'PH', 'Rings': 'SR', 'Vault': 'VT', 'P Bars': 'PB', 'H Bar': 'HB', 'AA': 'AA'}
    else:
        mapping = {'Vault': 'VT', 'Bars': 'UB', 'Beam': 'BB', 'Floor': 'FX', 'AA': 'AA'}
    
    # Rename columns that match our mapping
    for raw_col, clean_col in mapping.items():
        # Find column that contains the raw string (e.g. 'Vault' in 'Vault Score')
        match = next((c for c in df.columns if raw_col.lower() in str(c).lower()), None)
        if match:
            df = df.rename(columns={match: clean_col})
    
    # Keep only the columns we care about
    cols_to_keep = ['Athlete'] + list(mapping.values())
    df = df[[c for c in cols_to_keep if c in df.columns]]
    
    # Add Metadata
    df['Meet'] = meet
    df['Session'] = session
    df['Discipline'] = discipline
    
    # Clean all score columns
    for col in mapping.values():
        if col in df.columns:
            df[col] = df[col].apply(clean_score)
            
    return df

def main():
    # 1. Load targets from your primary CSV
    master_df = pd.read_csv(INPUT_CSV)
    targets = master_df[master_df['Date'].str.startswith('2026')].copy()
    
    all_sessions = []
    scraper = cloudscraper.create_scraper()

    for _, row in targets.iterrows():
        meet, sess, gymnast = row['Meet'], row['Session'], row['Gymnast']
        discipline = "Men" if gymnast == "Ansel" else "Women"
        
        print(f"🔄 Processing {meet} ({sess}) for {gymnast}...")

        # PATH A: MyMeetScores (Automated for Girls)
        if discipline == "Women" and meet in MMS_MEET_IDS and MMS_MEET_IDS[meet]:
            url = f"https://www.mymeetscores.com/meet.pl?meetid={MMS_MEET_IDS[meet]}&session={sess}"
            try:
                resp = scraper.get(url)
                tables = pd.read_html(StringIO(resp.text))
                for df in tables:
                    if any(x in str(df.columns).lower() for x in ['vault', 'gymnast']):
                        clean_df = parse_session_table(df, "Women", meet, sess)
                        all_sessions.append(clean_df)
                        print(f"   ✅ Scraped {len(clean_df)} athletes from MMS.")
                        break
            except Exception as e:
                print(f"   ❌ MMS Scrape failed: {e}")

        # PATH B: Local HTML (For Ansel/MSO)
        else:
            # Look for a file in ansel_history that matches this meet
            found_file = False
            for f in os.listdir(HTML_FOLDER):
                if sess in f and f.endswith(".html"):
                    try:
                        with open(os.path.join(HTML_FOLDER, f), 'r', encoding='utf-8') as file:
                            # MSO tables are often messy for read_html, so we use BeautifulSoup
                            soup = BeautifulSoup(file.read(), 'html.parser')
                            # Find the main results table
                            table = soup.find('table') 
                            if table:
                                df = pd.read_html(StringIO(str(table)))[0]
                                clean_df = parse_session_table(df, discipline, meet, sess)
                                all_sessions.append(clean_df)
                                print(f"   ✅ Parsed {len(clean_df)} athletes from local HTML.")
                                found_file = True
                                break
                    except Exception as e:
                        print(f"   ❌ HTML Parse failed: {e}")
            if not found_file:
                print(f"   ⚠️ No session HTML found for {meet} ({sess}) in {HTML_FOLDER}")

    if all_sessions:
        final_df = pd.concat(all_sessions, ignore_index=True)
        final_df.to_csv(OUTPUT_CSV, index=False)
        print(f"\n🎉 DONE! {OUTPUT_CSV} created with {len(final_df)} rows.")
    else:
        print("\n❌ Failed to collect any data.")

if __name__ == "__main__":
    main()
