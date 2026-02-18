import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import os
import re

CSV_FILE = "cleaned_gymnastics.csv"
HTML_FOLDER = "ansel_history"

def get_rank_from_mso(url):
    """Attempts to scrape Meet Rank from a live MSO URL"""
    scraper = cloudscraper.create_scraper()
    try:
        print(f"🌐 Scraping MSO: {url}")
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        meet_rank, meet_total = "", ""
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
        return meet_rank, meet_total
    except Exception as e:
        print(f"   ⚠️ Scrape failed: {e}")
        return None, None

def get_meta_from_html(folder):
    """Parses local HTML files to find Level, Div, Session for Ansel"""
    meta_map = {} # Maps (Gymnast, Meet) -> {Level, Div, Sess}
    for filename in os.listdir(folder):
        if filename.endswith(".html"):
            with open(os.path.join(folder, filename), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                
                # Extract identity
                gymnast = "Ansel" if "Ansel" in soup.title.get_text() else None
                if not gymnast: continue
                
                meet_name = soup.title.get_text().split(' - ')[1].split(',')[0].strip()
                
                # Extract Meta
                level, division, session = "", "", ""
                for li in soup.find_all('li'):
                    text = li.get_text(strip=True)
                    if "Level:" in text:
                        val = text.replace("Level:", "").strip()
                        if "D" in val:
                            parts = val.split('D', 1)
                            level, division = parts[0], "D" + parts[1]
                        else: level = val
                    if "Session:" in text: session = text.replace("Session:", "").strip()
                    if "Division:" in text: division = text.replace("Division:", "").strip()
                
                meta_map[(gymnast, meet_name)] = {'Level': level, 'Division': division, 'Session': session}
    return meta_map

def main():
    if not os.path.exists(CSV_FILE):
        print("❌ CSV not found.")
        return

    df = pd.read_csv(CSV_FILE)
    original_df = df.copy() # For comparison
    
    print(f"📋 Loaded {len(df)} rows. Starting audit...")

    # --- PART 1: FIX ROWS 2-17 (Annabelle/Azalea Meet Ranks) ---
    # We will use the URL you provided for the most recent Rose Gold meet
    # Note: If other rows need different URLs, we'd need a mapping
    girls_url = "https://meetscoresonline.com/results/36122/1314119"
    rank, total = get_rank_from_mso(girls_url)
    
    if rank:
        # Rows 2-17 (Indices 1 to 16 in Python)
        for i in range(1, 17):
            if i < len(df):
                df.at[i, 'Meet_Rank'] = rank
                df.at[i, 'Meet_Rank_Total'] = total

    # --- PART 2: FIX ROWS 18-25 (Ansel Metadata from HTML) ---
    local_meta = get_meta_from_html(HTML_FOLDER)
    for i in range(17, 25): # Indices 17 to 24
        if i < len(df):
            gymnast = df.at[i, 'Gymnast']
            meet = df.at[i, 'Meet']
            if (gymnast, meet) in local_meta:
                meta = local_meta[(gymnast, meet)]
                df.at[i, 'Level'] = meta['Level']
                df.at[i, 'Division'] = meta['Division']
                df.at[i, 'Session'] = meta['Session']

    # --- PART 3: AUDIT & SAVE ---
    print("\n--- 🔍 AUDIT RESULTS ---")
    changes_found = False
    for col in df.columns:
        diff = df[col] != original_df[col]
        if diff.any():
            changes_found = True
            count = diff.sum()
            print(f"✅ Updated '{col}': {count} cells changed.")
    
    if not changes_found:
        print("ℹ️ No changes needed. CSV matches requirements.")
    else:
        df.to_csv(CSV_FILE, index=False)
        print(f"\n🎉 Successfully updated and saved to {CSV_FILE}.")

if __name__ == "__main__":
    main()
