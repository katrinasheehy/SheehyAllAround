import pandas as pd
import cloudscraper
import os
from bs4 import BeautifulSoup
from io import StringIO
from meet_mapping import MMS_MEET_IDS, LOCAL_HTML_MAPPING

INPUT_CSV = "cleaned_gymnastics.csv"
OUTPUT_CSV = "session_raw_data.csv"
HTML_FOLDER = "session_html"

def parse_local_html(file_path, gymnast, meet, session):
    """Parses local HTML files (usually MSO) for a full session table."""
    print(f"📂 Parsing Local HTML: {os.path.basename(file_path)}")
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    rows = []
    # Targeted selector for MeetScoresOnline full results table rows
    for tr in soup.find_all('tr'):
        cells = tr.find_all('td')
        # Typical MSO row has Name, Team, then 4-6 event scores
        if len(cells) >= 6:
            row = {
                'Athlete': cells[0].get_text(strip=True),
                'VT': cells[5].get_text(strip=True) if len(cells) > 5 else "0.0",
                'UB': cells[6].get_text(strip=True) if len(cells) > 6 else "0.0",
                'BB': cells[7].get_text(strip=True) if len(cells) > 7 else "0.0",
                'FX': cells[8].get_text(strip=True) if len(cells) > 8 else "0.0",
                'AA': cells[-1].get_text(strip=True), # AA is usually last
                'Meet': meet,
                'Session': session,
                'Gymnast_Context': gymnast
            }
            rows.append(row)
    return pd.DataFrame(rows)

def scrape_mms(url, gymnast, meet, session):
    """Automatically scrapes MyMeetScores for a full level session."""
    scraper = cloudscraper.create_scraper()
    print(f"📡 Automating MyMeetScores: {meet} (Sess {session})")
    try:
        resp = scraper.get(url)
        # MMS tables are very clean and work well with read_html
        tables = pd.read_html(StringIO(resp.text))
        for df in tables:
            if any(col in df.columns for col in ['Vault', 'V', 'Gymnast']):
                df.rename(columns={'Gymnast':'Athlete','Vault':'VT','Bars':'UB','Beam':'BB','Floor':'FX'}, inplace=True)
                df['Meet'] = meet
                df['Session'] = session
                df['Gymnast_Context'] = gymnast
                return df
    except Exception as e:
        print(f"   ❌ MMS Scrape failed: {e}")
    return None

def main():
    if not os.path.exists(HTML_FOLDER): os.makedirs(HTML_FOLDER)
    df_history = pd.read_csv(INPUT_CSV)
    df_2026 = df_history[df_history['Date'].str.startswith('2026')].copy()
    
    all_data = []

    for _, row in df_2026.iterrows():
        key = (row['Gymnast'], row['Meet'])
        
        # 1. PRIORITY: MyMeetScores for Girls
        if row['Meet'] in MMS_MEET_IDS and MMS_MEET_IDS[row['Meet']]:
            url = f"https://www.mymeetscores.com/meet.pl?meetid={MMS_MEET_IDS[row['Meet']]}&session={row['Session']}"
            df = scrape_mms(url, row['Gymnast'], row['Meet'], row['Session'])
            if df is not None:
                all_data.append(df)
                continue

        # 2. FALLBACK: Local HTML for Ansel/MSO-Only
        html_file = LOCAL_HTML_MAPPING.get(key)
        if html_file and os.path.exists(os.path.join(HTML_FOLDER, html_file)):
            df = parse_local_html(os.path.join(HTML_FOLDER, html_file), row['Gymnast'], row['Meet'], row['Session'])
            if not df.empty:
                all_data.append(df)
                continue
            
        print(f"⏩ Skipping {row['Meet']} ({row['Gymnast']}) - Missing MMS ID or HTML file.")

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # Clean text scores (9.200 1 -> 9.200)
        for col in ['VT','UB','BB','FX','AA']:
            if col in final_df.columns:
                final_df[col] = final_df[col].astype(str).str.split(' ').str[0]
                final_df[col] = pd.to_numeric(final_df[col], errors='coerce')
        
        final_df.to_csv(OUTPUT_CSV, index=False)
        print(f"🎉 Process Complete! {len(final_df)} session rows gathered for analysis.")

if __name__ == "__main__":
    main()
