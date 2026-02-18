import pandas as pd
from bs4 import BeautifulSoup
import json
import os

# Configuration
SOURCE_FILE = "Ansel_Mas Watanabe_session.html"
OUTPUT_CSV = "ansel_mas_watanabe_raw.csv"

def extract_from_json_blob(soup):
    """
    MSO often hides the full results inside a JSON blob in the <script> tags.
    This is the most reliable way to get all 152 athletes.
    """
    for script in soup.find_all("script"):
        if script.string and "wbt.MeetInfo.Session" in script.string:
            # We are looking for the 'row' data inside the Session object
            try:
                # This regex-like find helps us isolate the JSON part
                start = script.string.find('wbt.MeetInfo.Session=') + len('wbt.MeetInfo.Session=')
                end = script.string.find('};', start) + 1
                json_data = json.loads(script.string[start:end])
                
                # Filter specifically for Level 4D1 as requested
                rows = json_data['result']['row']
                df = pd.DataFrame(rows)
                
                # Filter for the Level 4D1 session (Session 4)
                level_4d1_df = df[df['level'] == '4D1'].copy()
                return level_4d1_df
            except Exception as e:
                print(f"⚠️ JSON extraction failed: {e}")
    return pd.DataFrame()

def main():
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ File {SOURCE_FILE} not found.")
        return

    print(f"🚀 Parsing {SOURCE_FILE}...")
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # 1. Try JSON extraction (most complete for MSO)
    df = extract_from_json_blob(soup)

    if df.empty:
        print("⚠️ JSON extraction yielded no results. Checking for standard tables...")
        # Fallback to standard table parsing if JSON isn't available
        tables = pd.read_html(SOURCE_FILE)
        for table in tables:
            if 'Gymnast' in table.columns or 'Athlete' in table.columns:
                df = table
                break

    if not df.empty:
        # Standardize Columns to our design requirements
        # Note: Men's events: FX, PH, SR, VT, PB, HB
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ Success! Found {len(df)} athletes and saved to {OUTPUT_CSV}.")
        
        # Validation Check
        if len(df) == 152:
            print("🎯 Validation Pass: Found exactly 152 athletes.")
        else:
            print(f"📊 Note: Found {len(df)} athletes (expected 152).")
    else:
        print("❌ Could not find the results table in this HTML file.")

if __name__ == "__main__":
    main()
