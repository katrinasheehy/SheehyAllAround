import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
from io import StringIO
import re
import os
from datetime import datetime

# URL for Ansel's specific session (Age 9, Level 4D1)
ANSEL_URL = "https://meetscoresonline.com/results/36104/1306508#I4__4D1__9%20yrs"

def clean_and_split(val):
    """Splits '9.600 2' into (9.6, '2')"""
    if pd.isna(val) or not isinstance(val, str):
        return 0.0, ""
    match = re.match(r"(\d+\.\d+)\s*(.*)", str(val))
    if match:
        try:
            score = float(match.group(1))
            rank = match.group(2).strip()
            return score, rank
        except:
            return 0.0, ""
    return 0.0, ""

def scrape_ansel():
    print(f"🚀 Scraping Ansel's data from: {ANSEL_URL}")
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(ANSEL_URL)
        tables = pd.read_html(StringIO(response.text))
        
        ansel_row = None
        for df in tables:
            # Find the table row with "Ansel"
            if any(df.apply(lambda row: row.astype(str).str.contains('Ansel').any(), axis=1)):
                ansel_row = df[df.apply(lambda row: row.astype(str).str.contains('Ansel').any(), axis=1)].copy()
                break
        
        if ansel_row is None:
            print("❌ Could not find Ansel in the session tables.")
            return

        # Prepare the row for our "Universal Schema"
        # 1. Map MSO columns to our standard codes
        # Note: We map to 'Score' columns first, will split later
        col_map = {
            'FLOOR': 'FX_Raw', 'POMMEL': 'PH_Raw', 'RINGS': 'SR_Raw', 
            'VAULT': 'VT_Raw', 'PBARS': 'PB_Raw', 'HBAR': 'HB_Raw', 'AA': 'AA_Raw',
            'Gymnast': 'Gymnast_Name' # Temp name to avoid collision
        }
        ansel_row.rename(columns=col_map, inplace=True)
        
        # 2. Create a dictionary for the new clean row
        new_record = {
            'Date': datetime.now().strftime('%Y-%m-%d'), # Today's date for live scrape
            'Gymnast': 'Ansel',
            'Meet': 'Live Scraped Meet', # You can update this manually or scrape header
            'Session': '9 yrs',
            'Level': '4',
            'Division': 'D1'
        }
        
        # 3. Process Scores and Ranks
        events = ['FX', 'PH', 'SR', 'VT', 'PB', 'HB', 'AA']
        for evt in events:
            raw_col = evt + '_Raw'
            if raw_col in ansel_row.columns:
                val = ansel_row.iloc[0][raw_col]
                score, rank = clean_and_split(val)
                new_record[evt] = score
                new_record[evt + '_Rank'] = rank
            else:
                new_record[evt] = 0.0
                new_record[evt + '_Rank'] = ""

        # 4. Append to the Master File
        csv_file = "cleaned_gymnastics.csv"
        if os.path.exists(csv_file):
            history = pd.read_csv(csv_file)
            
            # Create a DataFrame for the new row
            new_df = pd.DataFrame([new_record])
            
            # Align columns (fill missing columns like 'UB' with 0/empty)
            for col in history.columns:
                if col not in new_df.columns:
                    new_df[col] = 0.0 if 'Rank' not in col else ""
            
            # Ensure column order matches
            new_df = new_df[history.columns]
            
            # Combine and Save
            updated_history = pd.concat([history, new_df], ignore_index=True)
            # Optional: Remove duplicates to prevent spamming the file if you run it twice
            updated_history.drop_duplicates(subset=['Gymnast', 'Date', 'Meet'], keep='last', inplace=True)
            
            updated_history.to_csv(csv_file, index=False)
            print("✅ Success! Ansel added to cleaned_gymnastics.csv with full details.")
            
    except Exception as e:
        print(f"❌ Error scraping: {e}")

if __name__ == "__main__":
    scrape_ansel()
