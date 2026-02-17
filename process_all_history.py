import pandas as pd
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

# Folder where you drop ALL html files (Ansel's, Annabelle's, Azalea's)
HTML_FOLDER = "ansel_history"
CSV_FILE = "cleaned_gymnastics.csv"

def parse_html_file(file_path):
    print(f"📄 Processing: {os.path.basename(file_path)}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return None

    # 1. IDENTIFY GYMNAST
    gymnast_name = "Unknown"
    if soup.title:
        title_text = soup.title.get_text()
        if "Ansel" in title_text: gymnast_name = "Ansel"
        elif "Annabelle" in title_text: gymnast_name = "Annabelle"
        elif "Azalea" in title_text: gymnast_name = "Azalea"
    
    if gymnast_name == "Unknown":
        print("   ⚠️ Could not identify gymnast from title. Skipping.")
        return None

    # 2. EXTRACT METADATA
    meet_name = "Unknown Meet"
    meet_date = datetime.now().strftime('%Y-%m-%d')
    
    if soup.title:
        parts = soup.title.get_text().split(' - ')
        if len(parts) >= 3:
            meet_name = parts[1].split(',')[0].strip()
            date_match = re.search(r"(\d{2}/\d{2}/\d{4})", soup.title.get_text())
            if date_match:
                meet_date = datetime.strptime(date_match.group(1), '%m/%d/%Y').strftime('%Y-%m-%d')

    # 3. EXTRACT MEET RANKING
    meet_rank = ""
    meet_total = ""
    for li in soup.find_all('li'):
        if "Meet Ranking" in li.get_text():
            rank_span = li.find('span', class_='bold')
            if rank_span:
                meet_rank = re.sub(r'\D', '', rank_span.get_text())
            
            italics = li.find('i')
            if italics:
                match = re.search(r"Out of (\d+)", italics.get_text())
                if match:
                    meet_total = match.group(1)
            break

    # 4. EXTRACT SCORES
    scores = {}
    table = soup.find('table', class_='table-condensed')
    if table:
        for row in table.find_all('tr'):
            th = row.find('th')
            td = row.find('td')
            if th and td:
                evt = th.get_text(strip=True)
                score_span = td.find('span', class_='score')
                rank_span = td.find('span', class_='place')
                
                if score_span:
                    val = float(score_span.get_text(strip=True))
                    rank = rank_span.get_text(strip=True) if rank_span else ""
                    
                    # Unified Mapping for Boys AND Girls
                    map_evt = {
                        'Floor': 'FX', 'Pommel': 'PH', 'Rings': 'SR', 
                        'Vault': 'VT', 'PBars': 'PB', 'HiBar': 'HB', 
                        'Bars': 'UB', 'Beam': 'BB', 'AA': 'AA'
                    }
                    
                    if evt in map_evt:
                        code = map_evt[evt]
                        scores[code] = val
                        scores[code+'_Rank'] = rank

    if not scores:
        print("   ⚠️ No scores found in table.")
        return None

    return {
        'Date': meet_date,
        'Gymnast': gymnast_name,
        'Meet': meet_name,
        'Meet_Rank': meet_rank,
        'Meet_Rank_Total': meet_total,
        **scores
    }

def main():
    if not os.path.exists(HTML_FOLDER):
        print(f"❌ Folder '{HTML_FOLDER}' not found.")
        return

    # Load existing CSV
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame()

    new_records = []
    
    # Process EVERY html file in the folder
    for filename in os.listdir(HTML_FOLDER):
        if filename.endswith(".html") or filename.endswith(".htm"):
            data = parse_html_file(os.path.join(HTML_FOLDER, filename))
            if data:
                new_records.append(data)

    if new_records:
        new_df = pd.DataFrame(new_records)
        
        # Merge with existing data
        # We use 'combine_first' logic: prefer the new data (with Meet Rank) over old data
        updated_df = pd.concat([df, new_df], ignore_index=True)
        
        # Deduplicate: If we have the same Gymnast/Meet/Score, keep the LAST one (the one we just parsed)
        # This effectively "upgrades" your old rows with the new Meet Rank data
        updated_df.drop_duplicates(subset=['Gymnast', 'Meet', 'AA'], keep='last', inplace=True)
        
        updated_df.to_csv(CSV_FILE, index=False)
        print(f"🎉 Success! Processed {len(new_records)} files. Historical data updated.")
    else:
        print("❌ No valid HTML files found.")

if __name__ == "__main__":
    main()
