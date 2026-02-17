import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
from io import StringIO
import re
import time

def clean_and_split(val):
if pd.isna(val) or not isinstance(val, str): return val, None
match = re.match(r"(\d+.\d+)\s*(.*)", str(val))
if match:
try:
score = float(match.group(1))
rank = match.group(2).strip()
return score, rank
except:
return val, None
return val, None

def get_all_tables(url, name):
print("Checking " + name + " profile...")
# Cloudscraper automatically handles the 'bot checks'
scraper = cloudscraper.create_scraper()
try:
response = scraper.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
valid_dfs = []
for table in soup.find_all('table'):
try:
# Use StringIO to satisfy the modern Pandas requirement
df = pd.read_html(StringIO(str(table)))[0]
if any(c in df.columns for c in ['AA', 'Vault', 'VT', 'Date']):
df['Gymnast'] = name
valid_dfs.append(df)
except:
continue
return pd.concat(valid_dfs, ignore_index=True) if valid_dfs else pd.DataFrame()
except Exception as e:
print("Error on " + name + ": " + str(e))
return pd.DataFrame()

profiles = {
"Annabelle": "",
"Azalea": "",
"Ansel": ""
}

all_data = []
for name, url in profiles.items():
data = get_all_tables(url, name)
if not data.empty:
all_data.append(data)
time.sleep(2)

if all_data:
master_df = pd.concat(all_data, ignore_index=True)
cols = {'Vault':'VT', 'Bars':'UB', 'Beam':'BB', 'Floor':'FX', 'Pommel Horse':'PH', 'Still Rings':'SR', 'Parallel Bars':'PB', 'High Bar':'HB'}
master_df.rename(columns=cols, inplace=True)
for c in ['VT','UB','BB','FX','PH','SR','PB','HB','AA']:
if c in master_df.columns:
cleaned = master_df[c].apply(clean_and_split)
master_df[c] = [x[0] for x in cleaned]
master_df[c + '_Rank'] = [x[1] for x in cleaned]
master_df.to_csv("gymnastics_history.csv", index=False)
print("Success! Check your csv file.")
else:
print("No data found. The site might be blocking this version of the scraper.")
