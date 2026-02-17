import streamlit as st
import pandas as pd
import plotly.express as px
import os

Set page to mobile-friendly centered layout
st.set_page_config(page_title="SheehyAllAround", layout="centered")

Custom CSS for the Pink and Purple themes
st.markdown("""

<style>
     annabelle-header { color: #FF69B4; font-size: 24px; font-weight: bold; }
     azalea-header { color: #9370DB; font-size: 24px; font-weight: bold; }
</style>

""", unsafe_allow_html=True)

def load_data():
    if os.path.exists("gymnastics_history.csv"):
        df = pd.read_csv("gymnastics_history.csv")
        # Ensure the date column is treated as a real date for the charts
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values(by='Date')
        return df
    return None

df = load_data()

st.title("🏆 Sheehy All-Around")

Create Tabs for the Girls
tab1, tab2 = st.tabs(["Annabelle (Pink)", "Azalea (Purple)"])

--- ANNABELLE SECTION ---
with tab1:
    st.markdown('<p class="annabelle-header">Annabelle - Level 3</p>', unsafe_allow_html=True)
    if df is not None:
        girl_df = df[df['Gymnast'].str.contains("Annabelle", na=False)]
        if not girl_df.empty:
            # Metric Cards for most recent meet
            latest = girl_df.iloc[-1]
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("VT", latest.get('VT', 0))
            col2.metric("UB", latest.get('UB', 0))
            col3.metric("BB", latest.get('BB', 0))
            col4.metric("FX", latest.get('FX', 0))
            
            # Line Chart for All-Around (AA) Progress
            st.subheader("Season AA Progress")
            fig = px.line(girl_df, x='Date', y='AA', markers=True,
                        labels={'AA': 'All-Around Score'},
                        color_discrete_sequence=['#FF69B4'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data found for Annabelle.")

--- AZALEA SECTION ---
with tab2:
....st.markdown('<p class="azalea-header">Azalea - Level 4</p>', unsafe_allow_html=True)
....if df is not None:
........girl_df = df[df['Gymnast'].str.contains("Azalea", na=False)]
........if not girl_df.empty:
............# Metric Cards for most recent meet
............latest = girl_df.iloc[-1]
............col1, col2, col3, col4 = st.columns(4)
............col1.metric("VT", latest.get('VT', 0))
............col2.metric("UB", latest.get('UB', 0))
............col3.metric("BB", latest.get('BB', 0))
............col4.metric("FX", latest.get('FX', 0))
............
............# Line Chart for All-Around (AA) Progress
............st.subheader("Season AA Progress")
............fig = px.line(girl_df, x='Date', y='AA', markers=True,
........................labels={'AA': 'All-Around Score'},
........................color_discrete_sequence=['#9370DB'])
............st.plotly_chart(fig, use_container_width=True)
........else:
............st.write("No data found for Azalea.")
