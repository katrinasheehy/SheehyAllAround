import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def scrape_gymnast_history(name, url):
    print(f"--- Scraping {name} ---")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    if "mymeetscores" in url:
        # MyMeetScores is usually table-heavy
        tables = pd.read_html(url)
        df = max(tables, key=len) # Grab the biggest table (the scores)
    else:
        # MeetScoresOnline often needs a session request
        response = requests.get(url, headers=headers)
        tables = pd.read_html(response.text)
        df = max(tables, key=len)

    df['Gymnast'] = name
    return df

# Your specific URLs
profiles = {
    "Annabelle_MMS": "https://www.mymeetscores.com/gymnast.pl?gymnastid=21874381",
    "Annabelle_MSO": "https://meetscoresonline.com/Athlete.MyScores/1314119",
    "Azalea_MMS": "https://www.mymeetscores.com/gymnast.pl?gymnastid=21817194",
    "Azalea_MSO": "https://meetscoresonline.com/Athlete.MyScores/1194621",
    "Ansel_MSO": "https://meetscoresonline.com/Athlete.MyScores/1306508"
}

all_history = []
for name, url in profiles.items():
    try:
        data = scrape_gymnast_history(name, url)
        all_history.append(data)
        time.sleep(2) # Be nice to the servers
    except Exception as e:
        print(f"Error on {name}: {e}")

# Combine and save
if all_history:
    final_df = pd.concat(all_history, ignore_index=True)
    final_df.to_csv("gymnastics_history.csv", index=False)
    print("✅ Success! Created gymnastics_history.csv")
