import pandas as pd
import re

def clean_gym_score(val):
    if pd.isna(val) or not isinstance(val, str):
        return val, None
    # Regex: Look for a decimal number (the score) and then the rest (the rank)
    match = re.match(r"(\d+\.\d+)\s*(.*)", str(val))
    if match:
        score = float(match.group(1))
        rank = match.group(2).strip()
        return score, rank
    return val, None

# Load the existing messy CSV
df = pd.read_csv("gymnastics_history.csv")

# Standardize Columns (Map 'Vault' -> 'VT', etc.)
column_map = {
    'Vault': 'VT', 'Bars': 'UB', 'Beam': 'BB', 'Floor': 'FX',
    'Pommel Horse': 'PH', 'Still Rings': 'SR', 'Parallel Bars': 'PB', 'High Bar': 'HB'
}
df = df.rename(columns=column_map)

# Apply the cleaning to all score columns
score_cols = ['VT', 'UB', 'BB', 'FX', 'PH', 'SR', 'PB', 'HB', 'AA']
for col in score_cols:
    if col in df.columns:
        # Create a new 'Rank' column for each event
        new_data = df[col].apply(clean_gym_score)
        df[col] = [x[0] for x in new_data]
        df[f'{col}_Rank'] = [x[1] for x in new_data]

# Save the cleaned version
df.to_csv("gymnastics_history.csv", index=False)
print("✅ Historical data cleaned and standardized!")
