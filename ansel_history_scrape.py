import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
import time

# Ansel's Athlete ID
ATHLETE_ID = "1306508"
PROFILE_URL = f"https://www.meetscoresonline.com/Athlete.MyScores/{ATHLETE_ID}"

def get_meet_links(scraper):
    """Scrapes the main profile to find all meet URLs"""
    print(f"🔍 Visiting Profile: {PROFILE_URL}")
    response = scraper.get(PROFILE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    meet_links = []
    
    # MSO lists meets in a table. We look for links that contain "/results/"
    # or specific "View Scores" buttons.
    # Note: MSO structure varies, but often the links look like: /results/MEET_ID/ATHLETE_ID
    for a in soup.find_all('a', href=True):
        if f"/results/" in a['href'] and ATHLETE_ID in a['href']:
            full_link = f"https://www.meetscoresonline.com{a['href']}"
            if full_link not in meet_links:
                meet_links.append(full_link)
    
    # Fallback: If no links found (likely due to JS), we might need to manually add them
    # But let's try this first.
    return meet_links

def clean_rank_text(text):
    """Extracts '36' from '36th'"""
    if not text: return ""
    match = re.search(r"(\d+)", str(text))
    return match.group(1) if match else ""

def scrape_single_meet(scraper, url):
    """Scrapes one specific meet page for scores AND Meet Rank"""
    print(f"   👉 Scraping meet: {url}")
    try:
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. EXTRACT SCORES (using the table logic we found earlier)
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
                        
                        # Map standard men's events
                        map_evt = {'Floor':'FX', 'Pommel':'PH', 'Rings':'SR', 'Vault':'VT', 'PBars':'PB', 'HiBar':'HB', 'AA':'AA'}
                        if evt in map_evt:
                            code = map_evt[evt]
                            scores[code] = val
                            scores[code+'_Rank'] = rank
        
        # 2. EXTRACT MEET RANKING ("36th out of 152")
        # Look for: <li class="text-center">Meet Ranking <span class="bold fs-2">36<sup>th</sup></span>
        meet_rank = ""
        meet_total = ""
        
        # Find the list item containing "Meet Ranking"
        for li in soup.find_all('li'):
            if "Meet Ranking" in li.get_text():
                # Get the rank (inside the span)
                rank_span = li.find('span', class_='bold')
                if rank_span:
                    meet_rank = clean_rank_text(rank_span.get_text())
                
                # Get the total (inside the 'i' tag usually: "Out of 152")
                italics = li.find('i')
                if italics:
                    total_text = italics.get_text() # "Out of 152 Level 4D1s"
                    match_total = re.search(r"Out of (\d+)", total_text)
                    if match_total:
                        meet_total = match_total.group(1)
                break

        # 3. EXTRACT METADATA (Date, Meet Name)
        meet_name = "Unknown Meet"
        meet_date = datetime.now().strftime('%Y-%m-%d')
        
        # Try to find date/name in title or header
        if soup.title:
            # Title often: "Ansel Sheehy - 2026 Mas Watanabe, CA 02/13/2026 - ..."
            title_text = soup.title.get_text()
            parts = title_text.split(' - ')
            if len(parts) >= 3:
                meet_name = parts[1].split(',')[0].strip() # "2026 Mas Watanabe"
                # Date extraction can be tricky, let's look for a date format
                date_match = re.search(r"(\d{2}/\d{2}/\d{4})", title_text)
                if date_match:
                    meet_date = datetime.strptime(date_match.group(1), '%m/%d/%Y').strftime('%Y-%m-%d')

        return {
            'scores': scores,
            'meta': {'Meet': meet_name, 'Date': meet_date, 'Meet_Rank': meet_rank, 'Meet_Rank_Total': meet_total}
        }

    except Exception as e:
        print(f"❌ Error scraping {url}: {e}")
        return None

def main():
    scraper = cloudscraper.create_scraper()
    
    # 1. Get List of Meets
    links = get_meet_links(scraper)
    
    # MANUAL FALLBACK: If the profile scraper fails (returns 0 links), 
    # paste the URLs you know here.
    if not links:
        print("⚠️ Auto-discovery failed (likely JS protection). Using manual list.")
        # Add the URL you gave me, plus any others you find on his page
        links = [
            "https://meetscoresonline.com/results/36104/1306508", # Mas Watanabe
            # "PASTE_OTHER_MEET_URLS_HERE",
        ]

    print(f"📋 Found {len(links)} meets to scrape.")
    
    csv_file = "cleaned_gymnastics.csv"
    if os.path.exists(csv_file):
        history = pd.read_csv(csv_file)
    else:
        history = pd.DataFrame()

    new_rows = []

    # 2. Loop through each meet
    for link in links:
        data = scrape_single_meet(scraper, link)
        if data and data['scores']:
            # Build the row
            record = {
                'Gymnast': 'Ansel',
                'Level': '4', # We might want to scrape this dynamically too if he was L3 before
                'Division': 'D1',
                'Date': data['meta']['Date'],
                'Meet': data['meta']['Meet'],
                'Meet_Rank': data['meta']['Meet_Rank'],
                'Meet_Rank_Total': data['meta']['Meet_Rank_Total']
            }
            record.update(data['scores'])
            new_rows.append(record)
            time.sleep(2) # Be polite to the server
            
    # 3. Save to CSV
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        # Combine
        updated_history = pd.concat([history, new_df], ignore_index=True)
        
        # Clean up duplicates (same gymnast, same meet)
        updated_history.drop_duplicates(subset=['Gymnast', 'Meet', 'AA'], keep='last', inplace=True)
        
        # Ensure all columns exist
        for col in updated_history.columns:
            if col not in updated_history.columns:
                updated_history[col] = 0.0

        updated_history.to_csv(csv_file, index=False)
        print(f"🎉 Successfully scraped {len(new_rows)} meets for Ansel!")
    else:
        print("❌ No data scraped.")

if __name__ == "__main__":
    main()
