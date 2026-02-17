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

# 3. Data Loading Logic
@st.cache_data
def load_data():
    if os.path.exists("gymnastics_history.csv"):
        df = pd.read_csv("gymnastics_history.csv")
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values(by='Date')
        return df
    return None

df = load_data()

# 4. Main UI
st.title("🏆 Sheehy All-Around")

tab1, tab2, tab3 = st.tabs(["Annabelle", "Azalea", "Ansel"])

# --- ANNABELLE (Pink / Level 3) ---
with tab1:
    st.markdown('<p class="annabelle-header">Annabelle - Level 3</p>', unsafe_allow_html=True)
    if df is not None:
        data = df[df['Gymnast'].str.contains("Annabelle", na=False)]
        if not data.empty:
            latest = data.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("VT", latest.get('VT', 0), "🏃‍♀️")
            c2.metric("UB", latest.get('UB', 0), "⚖️")
            c3.metric("BB", latest.get('BB', 0), "🪵")
            c4.metric("FX", latest.get('FX', 0), "🤸‍♀️")
            
            st.subheader("Season Progress")
            fig = px.line(data, x='Date', y='AA', markers=True, color_discrete_sequence=['#FF69B4'])
            st.plotly_chart(fig, use_container_width=True)

# --- AZALEA (Purple / Level 4) ---
with tab2:
    st.markdown('<p class="azalea-header">Azalea - Level 4</p>', unsafe_allow_html=True)
    if df is not None:
        data = df[df['Gymnast'].str.contains("Azalea", na=False)]
        if not data.empty:
            latest = data.iloc[-1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("VT", latest.get('VT', 0), "🏃‍♀️")
            c2.metric("UB", latest.get('UB', 0), "⚖️")
            c3.metric("BB", latest.get('BB', 0), "🪵")
            c4.metric("FX", latest.get('FX', 0), "🤸‍♀️")
            
            st.subheader("Season Progress")
            fig = px.line(data, x='Date', y='AA', markers=True, color_discrete_sequence=['#9370DB'])
            st.plotly_chart(fig, use_container_width=True)

# --- ANSEL (Teal / Level 4 Men's) ---
with tab3:
    st.markdown('<p class="ansel-header">Ansel - Level 4</p>', unsafe_allow_html=True)
    if df is not None:
        data = df[df['Gymnast'].str.contains("Ansel", na=False)]
        if not data.empty:
            latest = data.iloc[-1]
            # Men's 6-event layout
            r1c1, r1c2, r1c3 = st.columns(3)
            r2c1, r2c2, r2c3 = st.columns(3)
            r1c1.metric("FX", latest.get('FX', 0), "🤸‍♂️")
            r1c2.metric("PH", latest.get('PH', 0), "🐎")
            r1c3.metric("SR", latest.get('SR', 0), "⭕")
            r2c1.metric("VT", latest.get('VT', 0), "🏃‍♂️")
            r2c2.metric("PB", latest.get('PB', 0), "⏸️")
            r2c3.metric("HB", latest.get('HB', 0), "💈")
            
            st.subheader("Season Progress")
            fig = px.line(data, x='Date', y='AA', markers=True, color_discrete_sequence=['#008080'])
            st.plotly_chart(fig, use_container_width=True)
