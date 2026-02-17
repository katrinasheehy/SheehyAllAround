import pandas as pd
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

# Folder where you dropped the files
HTML_FOLDER = "ansel_history"
CSV_FILE = "cleaned_gymnastics.csv"

def extract_meet_data(file_path):
    print(f"📄 Processing: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 1. EXTRACT SCORES
    scores = {}
    table = soup.find('table', class_='table-condensed')
    if not table:
        print("   ⚠️ No score table found in this file.")
        return None

    for row in table.find_all('tr'):
        th = row.find('th')
        td = row.find('td')
        if th and td:
            evt_name = th.get_text(strip=True)
            score_span = td.find('span', class_='score')
            rank_span = td.find('span', class_='place')
            
            if score_span:
                val = float(score_span.get_text(strip=True))
                rank = rank_span.get_text(strip=True) if rank_span else ""
                
                # Map Names to Codes
                map_evt = {
                    'Floor': 'FX', 'Pommel': 'PH', 'Rings': 'SR', 
                    'Vault': 'VT', 'PBars': 'PB', 'HiBar': 'HB', 'AA': 'AA'
                }
                if evt_name in map_evt:
                    code = map_evt[evt_name]
                    scores[code] = val
                    scores[code+'_Rank'] = rank

    # 2. EXTRACT MEET RANKING (36th out of 152)
    meet_rank = ""
    meet_total = ""
    
    # Look for the list item with "Meet Ranking"
    for li in soup.find_all('li'):
        if "Meet Ranking" in li.get_text():
            # Rank is in bold span
            rank_span = li.find('span', class_='bold')
            if rank_span:
                meet_rank = re.sub(r'\D', '', rank_span.get_text()) # Remove 'th', 'nd'
            
            # Total is in italics usually
            italics = li.find('i')
            if italics:
                # Text looks like "Out of 152 Level 4D1s"
                match = re.search(r"Out of (\d+)", italics.get_text())
                if match:
                    meet_total = match.group(1)
            break

    # 3. EXTRACT METADATA
    # Try to find Meet Name and Date from Title
    meet_name = "Unknown Meet"
    meet_date = datetime.now().strftime('%Y-%m-%d')
    
    if soup.title:
        # Title format: "Ansel Sheehy - 2026 Mas Watanabe, CA 02/13/2026 - ..."
        title_text = soup.title.get_text()
        parts = title_text.split(' - ')
        if len(parts) >= 3:
            meet_name = parts[1].split(',')[0].strip()
            # Extract Date
            date_match = re.search(r"(\d{2}/\d{2}/\d{4})", title_text)
            if date_match:
                meet_date = datetime.strptime(date_match.group(1), '%m/%d/%Y').strftime('%Y-%m-%d')

    # 4. LEVEL & DIVISION
    # Look for "Level: 4D1" in the list
    level = "4"
    division = "D1"
    for li in soup.find_all('li'):
        if "Level:" in li.get_text():
             text = li.get_text().replace("Level:", "").strip()
             level = text # e.g. "4D1"
             break
             
    return {
        'Date': meet_date,
        'Gymnast': 'Ansel',
        'Meet': meet_name,
        'Level': level,
        'Division': division,
        'Meet_Rank': meet_rank,
        'Meet_Rank_Total': meet_total,
        **scores # Unpack scores into the dictionary
    }

def main():
    if not os.path.exists(HTML_FOLDER):
        print(f"❌ Folder '{HTML_FOLDER}' not found. Create it and add files!")
        return

    # Load existing CSV
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame()

    new_records = []
    
    # Process every file in folder
    for filename in os.listdir(HTML_FOLDER):
        if filename.endswith(".html") or filename.endswith(".htm"):
            data = extract_meet_data(os.path.join(HTML_FOLDER, filename))
            if data:
                new_records.append(data)

    if new_records:
        new_df = pd.DataFrame(new_records)
        
        # Combine
        updated_df = pd.concat([df, new_df], ignore_index=True)
        
        # Deduplicate (Keep the new version if we re-ran it)
        updated_df.drop_duplicates(subset=['Gymnast', 'Meet', 'AA'], keep='last', inplace=True)
        
        # Fill missing columns (NaN -> 0 or "")
        updated_df.fillna(0, inplace=True)
        
        updated_df.to_csv(CSV_FILE, index=False)
        print(f"🎉 Success! Processed {len(new_records)} meets and updated {CSV_FILE}.")
        print("You can now refresh your Streamlit app.")
    else:
        print("❌ No valid meet data found in the HTML files.")

if __name__ == "__main__":
    main()
