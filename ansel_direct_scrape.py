import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime

# URL for Ansel's specific session
URL = "https://meetscoresonline.com/results/36104/1306508"

def clean_score(val):
    """Splits '9.600 2' into (9.6, '2')"""
    if not val: return 0.0, ""
    match = re.search(r"(\d+\.\d+)\s*(\d+T?)?", str(val))
    if match:
        return float(match.group(1)), match.group(2) or ""
    return 0.0, ""

def scrape_ansel_direct():
    print(f"🚀 Attempting direct text scrape for Ansel...")
    scraper = cloudscraper.create_scraper()
    
    try:
        # Get the full page HTML
        response = scraper.get(URL)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # FIND ANSEL: Look for any HTML element containing "Ansel"
        # We search specifically for table rows (tr) first
        rows = soup.find_all('tr')
        ansel_row = None
        
        for row in rows:
            if "Ansel" in row.get_text():
                print(f"✅ Found Ansel's row!")
                ansel_row = row
                break
        
        if not ansel_row:
            # Fallback: Print what we DID find to help debug
            print("❌ Could not find 'Ansel' in any table row.")
            print("Page Title:", soup.title.string if soup.title else "No Title")
            return

        # EXTRACT DATA FROM THE ROW
        # We need to figure out which cell is which. 
        # Usually: Name | Team | FX | PH | SR | VT | PB | HB | AA
        cells = ansel_row.find_all('td')
        data_values = [c.get_text(strip=True) for c in cells]
        
        print("Raw Data Found:", data_values)
        
        # MAPPING (Adjust indices based on the printout above if needed)
        # Men's typical order: Name(0), Team(1), FX(2), PH(3), SR(4), VT(5), PB(6), HB(7), AA(8)
        # We need to be careful if there are extra columns (like Gymnast ID)
        
        # Let's assume standard order for now
        scores = {}
        # Try to map based on list length
        if len(data_values) >= 9:
            # FX is usually index 2 or 3 depending on if there is a 'Bib #' column
            # Let's assume Name is 0, Team is 1.
            start_idx = 2 
            events = ['FX', 'PH', 'SR', 'VT', 'PB', 'HB', 'AA']
            
            for i, evt in enumerate(events):
                if start_idx + i < len(data_values):
                    raw = data_values[start_idx + i]
                    s, r = clean_score(raw)
                    scores[evt] = s
                    scores[evt+'_Rank'] = r
        
        # CREATE THE RECORD
        new_record = {
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Gymnast': 'Ansel',
            'Meet': 'Live Scrape', # Placeholder
            'Level': '4',
            'Division': 'D1'
        }
        new_record.update(scores)
        
        # APPEND TO CSV
        csv_file = "cleaned_gymnastics.csv"
        if os.path.exists(csv_file):
            history = pd.read_csv(csv_file)
            new_df = pd.DataFrame([new_record])
            
            # Align columns
            for col in history.columns:
                if col not in new_df.columns:
                    new_df[col] = 0.0 if 'Rank' not in col else ""
            
            # Save
            updated = pd.concat([history, new_df], ignore_index=True)
            updated.to_csv(csv_file, index=False)
            print("✅ Ansel added to CSV!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    scrape_ansel_direct()
