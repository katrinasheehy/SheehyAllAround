import pandas as pd
import numpy as np

# Load the 655-row raw file you already verified
df = pd.read_csv("session_raw_data.csv")

# 1. DATA CLEANING
# Remove header/ad rows that snuck into the PDF scrape
df = df[df['Date'].str.contains('2026', na=False)]
df = df[~df['Gymnast'].str.contains('LIVE RESULTS', na=False)]

# Standardize strings to prevent grouping errors
df['Session'] = df['Session'].astype(str)
df['Level'] = df['Level'].astype(str)
df['Meet'] = df['Meet'].astype(str)

# Convert scores to numbers
score_cols = ["VT", "UB", "BB", "FX", "PH", "SR", "PB", "HB", "AA"]
df[score_cols] = df[score_cols].apply(pd.to_numeric, errors='coerce')

# Create a calculation frame where 0.0 is NaN for averages
calc_df = df.copy()
calc_df[score_cols] = calc_df[score_cols].replace(0.0, np.nan)

# 2. CALCULATE GROUP STATISTICS
# Session Stats (Median/Max per Event per Session)
session_stats = []
for (meet, sess, lvl), group in calc_df.groupby(['Meet', 'Session', 'Level']):
    for event in score_cols:
        valid = group[event].dropna()
        if not valid.empty:
            session_stats.append({
                'Meet': meet, 'Session': sess, 'Level': lvl, 'Event': event,
                'Median': valid.median(), 'Max': valid.max(), 'Count': len(valid)
            })
stats_df = pd.DataFrame(session_stats)

# Season Baseline (Average of Session Medians per Event per Level)
season_baseline = stats_df.groupby(['Level', 'Event'])['Median'].mean().to_dict()

# 3. GENERATE INDIVIDUAL CONTEXT FOR THE KIDS
child_map = {"Ansel": "Ansel Sheehy", "Annabelle": "Annabelle Sheehy", "Azalea": "Azalea Sheehy"}
final_rows = []

for nick, full_name in child_map.items():
    c_df = df[df['Gymnast'].str.contains(nick, case=False, na=False)]
    for _, row in c_df.iterrows():
        m, s, l = row['Meet'], row['Session'], row['Level']
        for event in score_cols:
            score = row[event]
            # Skip events they didn't compete in
            if pd.isna(score) or score == 0: continue
            
            # Get Session Context
            match = stats_df[(stats_df['Meet'] == m) & (stats_df['Session'] == s) & 
                             (stats_df['Level'] == l) & (stats_df['Event'] == event)]
            if match.empty: continue
            
            med = match['Median'].values[0]
            base = season_baseline.get((l, event))
            jsi = med - base if base else 0
            
            # Calculate Percentile (out of all valid scores in the session)
            all_scores = calc_df[(calc_df['Meet'] == m) & (calc_df['Session'] == s) & 
                                 (calc_df['Level'] == l)][event].dropna()
            percentile = (all_scores < score).mean() * 100
            
            final_rows.append({
                'Meet': m, 'Gymnast': full_name, 'Event': event, 'Score': score,
                'Median': med, 'Max': match['Max'].values[0], 'Count': int(match['Count'].values[0]),
                'Percentile': percentile, 'JSI': jsi
            })

# Save the final analytics file
results_df = pd.DataFrame(final_rows)
results_df.to_csv("session_context_analytics.csv", index=False)
print(f"✅ Analytics Complete: session_context_analytics.csv created with {len(results_df)} event records.")
