import pandas as pd
from bs4 import BeautifulSoup
import json
import os

# Configuration - Updated path to look in the subfolder
FOLDER = "ansel_history"
SOURCE_FILE = "Ansel_Mas Watanabe_session.html"
FULL_PATH = os.path.join(FOLDER, SOURCE_FILE)
OUTPUT_CSV = "ansel_mas_watanabe_raw.csv"

def main():
    # 1. Check if the folder exists
    if not os.path.exists(FOLDER):
        print(f"❌ Folder '{FOLDER}' not found in the current directory.")
        return

    # 2. List files to help debug if the name is slightly different
    print(f"📂 Checking folder '{FOLDER}'...")
    files = os.listdir(FOLDER)
    if SOURCE_FILE not in files:
        print(f"❌ File '{SOURCE_FILE}' NOT found.")
        print(f"🔍 I see these files in the folder: {files}")
        return

    print(f"🚀 Parsing {FULL_PATH}...")
    with open(FULL_PATH, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # MSO stores the full session data in a JSON blob inside a script tag
    found_data = False
    for script in soup.find_all("script"):
        if script.string and "wbt.MeetInfo.Session" in script.string:
            try:
                # Isolate the JSON data from the Javascript variable
                start = script.string.find('wbt.MeetInfo.Session=') + len('wbt.MeetInfo.Session=')
                end = script.string.find('};', start) + 1
                json_data = json.loads(script.string[start:end])
                
                # Extract the row data
                rows = json_data['result']['row']
                df = pd.DataFrame(rows)
                
                # Filter specifically for Level 4D1
                # (This ensures we get the 152 athletes you are expecting)
                df_4d1 = df[df['level'] == '4D1'].copy()
                
                df_4d1.to_csv(OUTPUT_CSV, index=False)
                print(f"✅ Success! Found {len(df_4d1)} athletes for Level 4D1.")
                print(f"💾 Saved to {OUTPUT_CSV}")
                found_data = True
                break
            except Exception as e:
                print(f"⚠️ Extraction error: {e}")

    if not found_data:
        print("❌ Could not extract the session data from the file.")

if __name__ == "__main__":
    main()
