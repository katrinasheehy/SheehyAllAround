import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="SheehyAllAround", layout="centered")

st.title("🏆 Sheehy All-Around (Debug Mode)")

# 1. Load Data Safely
if os.path.exists("gymnastics_history.csv"):
    try:
        # Read the file
        df = pd.read_csv("gymnastics_history.csv")
        
        # --- DEBUG SECTION: Show us the raw data ---
        st.subheader("1. Raw Data Preview")
        st.write("Here are the column names found in your file:")
        st.code(df.columns.tolist())  # This prints the EXACT list of headers
        
        st.write("Here is the first few rows of data:")
        st.dataframe(df.head())       # This shows the actual table
        
        # --- ATTEMPT TO FIX HEADERS ---
        # Strip invisible spaces
        df.columns = df.columns.str.strip()
        
        # Rename common variations to "AA"
        rename_map = {
            'All Around': 'AA', 'AllAround': 'AA', 'Total': 'AA', 
            'Score': 'AA', 'aa': 'AA', 'Total Score': 'AA'
        }
        df.rename(columns=rename_map, inplace=True)
        
        # Force AA to be numbers
        if 'AA' in df.columns:
            df['AA'] = pd.to_numeric(df['AA'], errors='coerce')
        
        # Handle Date
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.sort_values(by='Date')

    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        st.stop()
else:
    st.error("File 'gymnastics_history.csv' not found.")
    st.stop()

# 2. Tabs
tab1, tab2, tab3 = st.tabs(["Annabelle", "Azalea", "Ansel"])

def show_tab(name, color, events):
    st.header(f"{name}")
    
    # Filter for the gymnast
    # We use case=False so "annabelle" matches "Annabelle"
    subset = df[df['Gymnast'].str.contains(name, case=False, na=False)].copy()
    
    if not subset.empty:
        # Show Metrics
        latest = subset.iloc[-1]
        cols = st.columns(len(events))
        for i, (evt, icon) in enumerate(events.items()):
            # Use .get() so it never crashes if a column is missing
            val = latest.get(evt, "-")
            cols[i].metric(evt, val)
        
        # Show Chart ONLY if AA exists
        if 'AA' in subset.columns:
            # Drop empty rows
            chart_data = subset.dropna(subset=['AA'])
            if not chart_data.empty:
                fig = px.line(chart_data, x='Date', y='AA', markers=True, 
                              color_discrete_sequence=[color], title=f"{name}'s Progress")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"Found data for {name}, but the 'AA' column has no valid numbers.")
        else:
            st.warning("⚠️ Could not find an 'AA' column. Check the 'Raw Data Preview' above to see what it's named!")
            
        # Show the table for this kid specifically
        with st.expander(f"See Raw Data for {name}"):
            st.dataframe(subset)
            
    else:
        st.warning(f"No rows found with Gymnast name '{name}'")

# --- DRAW TABS ---
with tab1:
    show_tab("Annabelle", "#FF69B4", {'VT':'🏃‍♀️', 'UB':'⚖️', 'BB':'🪵', 'FX':'🤸‍♀️'})

with tab2:
    show_tab("Azalea", "#9370DB", {'VT':'🏃‍♀️', 'UB':'⚖️', 'BB':'🪵', 'FX':'🤸‍♀️'})

with tab3:
    show_tab("Ansel", "#008080", {'FX':'🤸‍♂️', 'PH':'🐎', 'SR':'⭕', 'VT':'🏃‍♂️', 'PB':'⏸️', 'HB':'💈'})
