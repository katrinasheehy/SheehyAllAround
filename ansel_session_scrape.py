import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
from io import StringIO
import re
import os

def clean_and_split(val):
if pd.isna(val) or not isinstance(val, str): return val, None
match = re.match(r"(\d+.\d+)\s*(.*)", str(val))
return (float(match.group(1)), match.group(2).strip()) if match else (val, None)

def scrape_and_update():
url = ""
print("🚀 Fetching Ansel's session data...")

scrape_and_update()
