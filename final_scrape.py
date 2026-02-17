from io import StringIO
import pandas as pd
import requests
import re

def clean_and_split(val):
    """Splits '9.425 3T' into (9.425, '3T')"""
    if pd.isna(val) or not isinstance(val, str): return val, None
    match = re.match(r"(\d+\.\d+)\s*(.*)", str(val))
    return (float(match.group(1)), match.group(2).strip()) if match else (val, None)

def get_all_tables(url, name):
    print(f"Scraping all data for {name}...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    all_tables = pd.read_html(StringIO(response.text))
    
    valid_dfs = []
    for df in all_tables:
        # Check if this table actually contains scores
        if 'AA' in df.columns or 'All Around' in df.columns:
            df['Gymnast'] = name
            valid_dfs.append(df)
    
    return pd.concat(valid_dfs, ignore_index=True) if valid_dfs else pd.DataFrame()

# Updated URLs
profiles = {
    "Annabelle": "https://meetscoresonline.com/Athlete.MyScores/1314119",
    "Azalea": "https://meetscoresonline.com/Athlete.MyScores/1194621",
    "Ansel": "https://meetscoresonline.com/Athlete.MyScores/1306508"
}

# 1. Scrape everything
final_list = [get_all_tables(url, name) for name, url in profiles.items()]
master_df = pd.concat(final_list, ignore_index=True)

# 2. Clean the score/rank mess
score_cols = ['Vault', 'Bars', 'Beam', 'Floor', 'Pommel Horse', 'Still Rings', 'Parallel Bars', 'High Bar', 'AA']
for col in score_cols:
    if col in master_df.columns:
        cleaned = master_df[col].apply(clean_and_split)
        master_df[col] = [x[0] for x in cleaned]
        master_df[f'{col}_Rank'] = [x[1] for x in cleaned]

master_df.to_csv("gymnastics_history.csv", index=False)
print("✅ Done! Ansel found and data cleaned.")
