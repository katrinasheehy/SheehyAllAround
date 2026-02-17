import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="SheehyAllAround", layout="centered")

# 2. Custom Styling
st.markdown("""
    <style>
    .annabelle-header { color: #FF69B4; font-size: 26px; font-weight: bold; }
    .azalea-header { color: #9370DB; font-size: 26px; font-weight: bold; }
    .ansel-header { color: #008080; font-size: 26px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading & Cleaning
@st.cache_data
def load_data():
    if os.path.exists("gymnastics_history.csv"):
        try:
            df = pd.read_csv("gymnastics_history.csv")
            
            # --- CRITICAL FIX: Standardize Column Names ---
            # Map full words to the short codes the app uses
            rename_map = {
                'Vault': 'VT',
                'Bars': 'UB',
                'Beam': 'BB',
                'Floor': 'FX',
                'Pommel': 'PH',
                'Rings': 'SR',
                'PBar': 'PB',
                'HighBar': 'HB',
                'AA': 'AA' 
            }
            df.rename(columns=rename_map, inplace=True)
            
            # Force AA to be numeric (turns "36.500(1)" into NaN)
            if 'AA' in df.columns:
                df['AA'] = pd.to_numeric(df['AA'], errors='coerce')
            
            # Handle Date
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df = df.sort_values(by='Date')
                
            return df
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return None
    return None

df = load_data()

# 4. Main UI
st.title("🏆 Sheehy All-Around")

tab1, tab2, tab3 = st.tabs(["Annabelle", "Azalea", "Ansel"])

# Helper function to prevent repetitive code
def show_gymnast_tab(name, color, events, header_class):
    st.markdown(f'<p class="{header_class}">{name}</p>', unsafe_allow_html=True)
    if df is not None:
        # Filter data for this gymnast (Case insensitive)
        data = df[df['Gymnast'].str.contains(name, case=False, na=False)].copy()
        
        if not data.empty:
            # Metrics Row (Most Recent Meet)
            latest = data.iloc[-1]
            cols = st.columns(len(events))
            for i, (event_code, icon) in enumerate(events.items()):
                # Use .get() to safely grab data even if column is missing
                val = latest.get(event_code, "-")
                cols[i].metric(event_code, val)
            
            # Line Chart
            st.subheader("Season Progress")
            # Only plot if we actually have valid AA numbers
            chart_data = data.dropna(subset=['AA'])
            
            if not chart_data.empty:
                fig = px.line(chart_data, x='Date', y='AA', markers=True, 
                              color_discrete_sequence=[color])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No All-Around scores available for the chart yet.")
        else:
            st.warning(f"No data found for {name}.")

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
    # Note: Ansel might need different mapping if his columns are different
    events_boys = {'FX': '🤸‍♂️', 'PH': '🐎', 'SR': '⭕', 'VT': '🏃‍♂️', 'PB': '⏸️', 'HB': '💈'}
    show_gymnast_tab("Ansel", "#008080", events_boys, "ansel-header")
    
