import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="SheehyAllAround", layout="centered", page_icon="🤸")

# 2. Custom Styling
st.markdown("""
    <style>
    .annabelle-header { color: #FF69B4; font-size: 28px; font-weight: bold; }
    .azalea-header { color: #9370DB; font-size: 28px; font-weight: bold; }
    .ansel-header { color: #008080; font-size: 28px; font-weight: bold; }
    .metric-card { background-color: #f0f2f6; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. Robust Data Loading
@st.cache_data
def load_data():
    file_path = "cleaned_gymnastics.csv"
    if not os.path.exists(file_path):
        return None

    try:
        df = pd.read_csv(file_path)
        
        # --- CLEANING STEP 1: Standardize Column Names ---
        df.columns = df.columns.str.strip() # Remove hidden spaces
        
        # Map ALL possible variations to the standard short codes
        rename_map = {
            'Vault': 'VT', 'Bars': 'UB', 'Beam': 'BB', 'Floor': 'FX',
            'Pommel': 'PH', 'Rings': 'SR', 'PBar': 'PB', 'PBars': 'PB', 'HighBar': 'HB', 'HiBar': 'HB',
            'All Around': 'AA', 'Total': 'AA', 'Score': 'AA',
            'Meet Ranking': 'Meet_Rank', 'Rank': 'Meet_Rank'
        }
        df.rename(columns=rename_map, inplace=True)

        # --- CLEANING STEP 2: Force Numbers ---
        # List of columns that MUST be numbers
        score_cols = ['VT', 'UB', 'BB', 'FX', 'PH', 'SR', 'PB', 'HB', 'AA']
        
        for col in score_cols:
            if col in df.columns:
                # Coerce errors: turns "9.500 (1)" or "text" into NaN, but keeps "9.5"
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # --- CLEANING STEP 3: Handle Dates ---
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.sort_values(by='Date')

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

df = load_data()

# 4. Main Dashboard UI
st.title("🏆 Sheehy All-Around")

if df is None:
    st.warning("⚠️ No data file found (`cleaned_gymnastics.csv`). Please run the scraper first.")
    st.stop()

# TABS
tab1, tab2, tab3 = st.tabs(["Annabelle", "Azalea", "Ansel"])

def show_gymnast_tab(name, color, events, header_class):
    st.markdown(f'<p class="{header_class}">{name}</p>', unsafe_allow_html=True)
    
    # Filter for the specific gymnast
    # We use 'str.contains' to be safe (matches "Ansel" in "Ansel Sheehy")
    subset = df[df['Gymnast'].astype(str).str.contains(name, case=False, na=False)].copy()
    
    if not subset.empty:
        # Get the Most Recent Meet
        latest = subset.iloc[-1]
        
        # --- TOP ROW: Context ---
        m1, m2 = st.columns([2, 1])
        m1.info(f"📍 **Latest Meet:** {latest.get('Meet', 'Unknown')} ({latest.get('Date', '').date()})")
        
        # Meet Rank Badge (if available)
        rank = latest.get('Meet_Rank', '')
        total = latest.get('Meet_Rank_Total', '')
        if pd.notna(rank) and str(rank) != "" and str(rank) != "0" and str(rank) != "nan":
            rank_display = f"{int(float(rank))} / {int(float(total))}" if pd.notna(total) and total != "" else f"{int(float(rank))}"
            m2.metric("🏆 Meet Rank", rank_display)
        else:
            m2.write("") # Spacer

        # --- SCORES ROW ---
        # Dynamic columns based on number of events
        cols = st.columns(len(events))
        for i, (evt_code, icon) in enumerate(events.items()):
            val = latest.get(evt_code, None)
            
            # Formatting: If it's a number, format to 3 decimals. If NaN, show "-"
            if pd.notna(val):
                display_val = f"{val:.3f}"
            else:
                display_val = "-"
            
            cols[i].metric(f"{evt_code}", display_val, icon)
            
        # --- AA SCORE ---
        aa_val = latest.get('AA', None)
        if pd.notna(aa_val):
            st.metric("All-Around (AA)", f"{aa_val:.3f}")
            
        # --- CHART ---
        st.subheader("📈 Season Progress")
        chart_data = subset.dropna(subset=['AA'])
        if not chart_data.empty:
            fig = px.line(chart_data, x='Date', y='AA', markers=True, 
                          title=f"{name}'s All-Around Score Trend",
                          color_discrete_sequence=[color])
            fig.update_layout(yaxis_title="Score", xaxis_title="Date")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data points for a progress chart yet.")

        # --- DEBUG: RAW DATA ---
        with st.expander(f"🔍 Inspect Raw Data for {name}"):
            st.dataframe(subset)

    else:
        st.info(f"No data found for {name}. Check the CSV or spelling!")

# --- ANNABELLE (Pink) ---
with tab1:
    events_girls = {'VT': '🏃‍♀️', 'UB': '⚖️', 'BB': '🪵', 'FX': '🤸‍♀️'}
    show_gymnast_tab("Annabelle", "#FF69B4", events_girls, "annabelle-header")

# --- AZALEA (Purple) ---
with tab2:
    events_girls = {'VT': '🏃‍♀️', 'UB': '⚖️', 'BB': '🪵', 'FX': '🤸‍♀️'}
    show_gymnast_tab("Azalea", "#9370DB", events_girls, "azalea-header")

# --- ANSEL (Teal) ---
with tab3:
    events_boys = {'FX': '🤸‍♂️', 'PH': '🐎', 'SR': '⭕', 'VT': '🏃‍♂️', 'PB': '⏸️', 'HB': '💈'}
    show_gymnast_tab("Ansel", "#008080", events_boys, "ansel-header")
