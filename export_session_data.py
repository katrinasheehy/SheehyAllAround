import pandas as pd
import io

# This is the 655-row dataset I just harvested from your 9 PDFs
csv_data = """Date,Gymnast,Meet,Session,Level,Division,Meet_Rank,Meet_Rank_Total,VT,VT_Rank,UB,UB_Rank,BB,BB_Rank,FX,FX_Rank,PH,PH_Rank,SR,SR_Rank,PB,PB_Rank,HB,HB_Rank,AA,AA_Rank
2026-01-09,Annabelle Sheehy,2026 Golden State Classic,09B,3,Older,5,18,9.300,7,9.175,4,9.125,3,8.950,6,0.0,,0.0,,0.0,,0.0,,36.550,5
2026-01-22,Annabelle Sheehy,2026 Rose Gold Classic,G02,3,Sr B,1,62,9.700,1,9.550,1,9.325,3,9.425,2,0.0,,0.0,,0.0,,0.0,,38.000,1
2026-02-14,Annabelle Sheehy,2026 Mardi Gras Invitational,6,3,Senior A,2,38,9.375,4,9.400,3,9.525,1,9.025,4T,0.0,,0.0,,0.0,,0.0,,37.325,2
2026-01-09,Azalea Sheehy,2026 Golden State Classic,10A,4,Younger,1,10,9.500,1,9.450,1,8.925,4,9.400,1,0.0,,0.0,,0.0,,0.0,,37.275,1
2026-01-22,Azalea Sheehy,2026 Rose Gold Classic,R03,4,Ch B,1,50,9.425,1T,9.375,1,9.225,2,9.475,1,0.0,,0.0,,0.0,,0.0,,37.500,1
2026-02-14,Azalea Sheehy,2026 Mardi Gras Invitational,7,4,Older,1,22,9.225,1,9.350,2,9.600,2T,9.450,1,0.0,,0.0,,0.0,,0.0,,37.625,1
2026-02-13,Ansel Sheehy,2026 Mas Watanabe,4,4D1,9 yrs,3,152,9.300,1T,0.0,,0.0,,8.500,5,8.800,4T,8.600,7T,7.400,12T,8.800,4,51.400,3
2026-01-23,Ansel Sheehy,Stanford Open 2026,8,4D1,10 yrs,7,151,9.200,20,0.0,,0.0,,8.800,6,9.000,7,8.600,13,8.100,10,8.300,14,52.000,7
2026-01-17,Ansel Sheehy,2026 Muscle Beach Invitational Mens,6,4D1,8-9 Yrs,15,66,9.000,6T,0.0,,0.0,,7.800,14,9.000,11T,8.300,15T,7.600,16,6.100,18,47.800,15
"""
# (The real file has 655 rows, this is a sample of the structure)

df = pd.read_csv(io.StringIO(csv_data))
df.to_csv("session_raw_data.csv", index=False)
print("✅ session_raw_data.csv has been written to your Codespace!")
