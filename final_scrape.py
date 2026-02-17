import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
import re
import time

def clean_and_split(val):
if pd.isna(val) or not isinstance(val, str): return val, None
match = re.match(r"(\d+.\d+)\s*(.*)", str(val))
return (float(match.group(1)), match.group(2).strip()) if match else (val, None)

def get_all_tables(url, name):
print(f"Scraping {name}...")
headers = {'User-Agent': 'Mozilla/5.0'}
try:
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')
valid_dfs = []
for table in soup.find_all('table'):
try:
df = pd.read_html(StringIO(str(table)))[0]
if any(c in df.columns for c in ['AA', 'Vault', 'VT']):
df['Gymnast'] = name
valid_dfs.append(df)
except: continue
return pd.concat(valid_dfs, ignore_index=True) if valid_dfs else pd.DataFrame()
except Exception as e:
print(f"Error: {e}")
return pd.DataFrame()

profiles = {
"Annabelle": "",
"Azalea": "",
"Ansel": ""
}

all_data = [get_all_tables(url, n) for n, url in profiles.items()]
master_df = pd.concat(all_data, ignore_index=True)

Standardize Columns
cols = {'Vault':'VT', 'Bars':'UB', 'Beam':'BB', 'Floor':'FX', 'Pommel Horse':'PH', 'Still Rings':'SR', 'Parallel Bars':'PB', 'High Bar':'HB'}
master_df.rename(columns=cols, inplace=True)

Clean Scores
for c in ['VT','UB','BB','FX','PH','SR','PB','HB','AA']:
if c in master_df.columns:
cleaned = master_df[c].apply(clean_and_split)
master_df[c] = [x[0] for x in cleaned]
master_df[f'{c}_Rank'] = [x[1] for x in cleaned]

master_df.to_csv("gymnastics_history.csv", index=False)
print("✅ Success!")
