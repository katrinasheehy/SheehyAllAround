import pandas as pd
import os

def upgrade_csv_schema():
    csv_file = "cleaned_gymnastics.csv"
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        print(f"🔧 Upgrading {csv_file} schema...")
        
        # Add new columns if they don't exist
        if 'Meet_Rank' not in df.columns:
            df['Meet_Rank'] = "" # Rank (e.g., 36)
        if 'Meet_Rank_Total' not in df.columns:
            df['Meet_Rank_Total'] = "" # Total gymnasts (e.g., 152)
            
        # Re-order columns to look nice
        # We put the new ranks right after the "Division"
        cols = ['Date', 'Gymnast', 'Meet', 'Session', 'Level', 'Division', 
                'Meet_Rank', 'Meet_Rank_Total',
                'VT', 'VT_Rank', 'UB', 'UB_Rank', 'BB', 'BB_Rank', 'FX', 'FX_Rank', 
                'PH', 'PH_Rank', 'SR', 'SR_Rank', 'PB', 'PB_Rank', 'HB', 'HB_Rank',
                'AA', 'AA_Rank']
        
        # Only keep columns that actually exist in the dataframe
        final_cols = [c for c in cols if c in df.columns]
        df = df[final_cols]
        
        df.to_csv(csv_file, index=False)
        print("✅ Success! Added 'Meet_Rank' columns to the file.")
    else:
        print("❌ Could not find cleaned_gymnastics.csv. Run the previous cleaner first.")

if __name__ == "__main__":
    upgrade_csv_schema()
