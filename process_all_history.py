import pandas as pd
from bs4 import BeautifulSoup
import os
import re
from datetime import datetime

# Folder where you drop ALL html files
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

    # 2. EXTRACT MEET NAME & DATE
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

    # 3. EXTRACT LEVEL, DIVISION, SESSION
    # Look for list items like <li><span class="title">Level: </span>4D1</li>
    level = ""
    division = ""
    session = ""
    
    # We search all list items <li> because MSO puts this info in a 'card'
    for li in soup.find_all('li'):
        text = li.get_text(strip=True)
        
        # LEVEL & DIVISION
        if "Level:" in text:
            # text looks like "Level: 4D1"
            full_level_str = text.replace("Level:", "").strip()
            
            # SPLIT LOGIC: often "4D1" means Level 4, Div D1
            # Let's try to be smart about it.
            if "D" in full_level_str and full_level_str[0].isdigit():
                # Split "4D1" into Level="4", Div="D1"
                parts = full_level_str.split('D', 1)
                level = parts[0]
                division = "D" + parts[1]
            else:
                # Just keep the whole thing as Level if unsure
                level = full_level_str
        
        # SESSION (Sometimes labeled "Session:" or found in specific spans)
        if "Session:" in text:
            session = text.replace("Session:", "").strip()
        
        # DIVISION (Sometimes explicitly labeled)
        if "Division:" in text or "Div:" in text:
            val = text.replace("Division:", "").replace("Div:", "").strip()
            if val: division = val

    # 4. EXTRACT MEET RANKING (e.g. "36th out of 152")
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

    # 5. EXTRACT SCORES
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
                    
                    # Unified Mapping
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

    # Construct Record
    return {
        'Date': meet_date,
        'Gymnast': gymnast_name,
        'Meet': meet_name,
        'Session': session,
        'Level': level,
        'Division': division,
        'Meet_Rank': meet_rank,
        'Meet_Rank_Total': meet_total,
        **scores
    }

def main():
    if not os.path.exists(HTML_FOLDER):
        print(f"❌ Folder '{HTML_FOLDER}' not found.")
        return

    # Load existing CSV or create new
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame()

    new_records = []
    
    # Process EVERY html file
    for filename in os.listdir(HTML_FOLDER):
        if filename.endswith(".html") or filename.endswith(".htm"):
            data = parse_html_file(os.path.join(HTML_FOLDER, filename))
            if data:
                new_records.append(data)

    if new_records:
        new_df = pd.DataFrame(new_records)
        
        # Merge logic:
        # We assume the HTML files are the "Source of Truth". 
        # So we append them to the existing CSV, then deduplicate keeping the NEW ones.
        updated_df = pd.concat([df, new_df], ignore_index=True)
        
        # Deduplicate based on Gymnast + Meet + AA score
        # keep='last' ensures the rows we just parsed (with Level/Div) replace the old ones
        updated_df.drop_duplicates(subset=['Gymnast', 'Meet', 'AA'], keep='last', inplace=True)
        
        # Fill NaNs with blanks/zeros so the CSV looks clean
        updated_df.fillna("", inplace=True)
        
        updated_df.to_csv(CSV_FILE, index=False)
        print(f"🎉 Success! Updated {len(new_records)} meets with Level, Division, and Session info.")
    else:
        print("❌ No HTML files found to process.")

if __name__ == "__main__":
    main()
