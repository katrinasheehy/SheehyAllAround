import pandas as pd
import cloudscraper
import os
from bs4 import BeautifulSoup
from io import StringIO
from meet_mapping import MMS_MEET_IDS

INPUT_CSV = "cleaned_gymnastics.csv"
OUTPUT_CSV = "session_raw_data.csv"
ANSEL_FOLDER = "ansel_history"

def parse_mso_session_html(file_path):
    """Parses local MSO session HTML for both Men's and Women's layouts."""
    print(f"📂 Parsing Local Session: {os.path.basename(file_path)}")
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    rows = []
    # Identify table rows with gymnast data
    for tr in soup.find_all('tr', {'data-gymnastid': True}) or soup.find_all('tr'):
        cells = tr.find_all('td')
        if len(cells) < 6: continue
        
        name = cells[0].get_text(strip=True)
        # Check if it looks like a Men's 6-event table (typically more columns)
        if len(cells) >= 10: 
            row = {
                'Athlete': name,
                'FX': cells[2].get_text(strip=True),
                'PH': cells[3].get_text(strip=True),
                'SR': cells[4].get_text(strip=True),
                'VT': cells[5].get_text(strip=True),
                'PB': cells[6].get_text(strip=True),
                'HB': cells[7].get_text(strip=True),
                'AA': cells[-1].get_text(strip=True),
                'Source_File': os.path.basename(file_path)
            }
        else: # Women's 4-event
            row = {
                'Athlete': name,
                'VT': cells[5].get_text(strip=True) if len(cells)>5 else "0",
                'UB': cells[6].get_text(strip=True) if len(cells)>6 else "0",
                'BB': cells[7].get_text(strip=True) if len(cells)>7 else "0",
                'FX': cells[8].get_text(strip=True) if len(cells)>8 else "0",
                'AA': cells[-1].get_text(strip=True),
                'Source_File': os.path.basename(file_path)
            }
        rows.append(row)
    return pd.DataFrame(rows)

def main():
    df_history = pd.read_csv(INPUT_CSV)
    df_2026 = df_history[df_history['Date'].str.startswith('2026')].copy()
    all_data = []

    # 1. GIRLS: Auto-Scrape MyMeetScores
    scraper = cloudscraper.create_scraper()
    for _, row in df_2026.iterrows():
        m_name = row['Meet']
        if m_name in MMS_MEET_IDS and MMS_MEET_IDS[m_name]:
            url = f"https://www.mymeetscores.com/meet.pl?meetid={MMS_MEET_IDS[m_name]}&session={row['Session']}"
            print(f"📡 Scraping MMS: {m_name} (Sess {row['Session']})")
            try:
                resp = scraper.get(url)
                tables = pd.read_html(StringIO(resp.text))
                for df in tables:
                    if 'Gymnast' in df.columns or 'Vault' in df.columns:
                        df.rename(columns={'Gymnast':'Athlete','Vault':'VT','Bars':'UB','Beam':'BB','Floor':'FX'}, inplace=True)
                        df['Meet'] = m_name
                        df['Session'] = row['Session']
                        all_data.append(df)
            except: pass

    # 2. ANSEL: Dynamic Local Scan
    if os.path.exists(ANSEL_FOLDER):
        for f in os.listdir(ANSEL_FOLDER):
            if "_session" in f and f.endswith(".html"):
                df_local = parse_mso_session_html(os.path.join(ANSEL_FOLDER, f))
                if not df_local.empty:
                    # Map the filename back to the meet if possible
                    df_local['Meet'] = f.replace('_session.html', '').replace('_', ' ').title()
                    all_data.append(df_local)

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Clean scores: "9.200 1" -> 9.2
        cols = ['VT','UB','BB','FX','PH','SR','PB','HB','AA']
        for c in cols:
            if c in final_df.columns:
                final_df[c] = final_df[c].astype(str).str.split(' ').str[0]
                final_df[c] = pd.to_numeric(final_df[c], errors='coerce').fillna(0)
        
        final_df.to_csv(OUTPUT_CSV, index=False)
        print(f"🎉 Done! {len(final_df)} rows of raw context saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
