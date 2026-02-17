import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Config for Mobile
st.set_page_config(page_title="SheehyAllAround", layout="centered")

# Custom CSS for the color themes
st.markdown("""
    <style>
    .annabelle-header { color: #FF69B4; font-weight: bold; }
    .azalea-header { color: #9370DB; font-weight: bold; }
    .ansel-header { color: #008080; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Sheehy All-Around")

# 2. Sidebar / Navigation
tabs = st.tabs(["Annabelle", "Azalea", "Ansel", "Team Overview"])

# --- ANNABELLE (Level 3 - Pink) ---
with tabs[0]:
    st.markdown('<h2 class="annabelle-header">Annabelle - Level 3</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("VT", "---", "🏃‍♀️")
    col2.metric("UB", "---", "⚖️")
    col3.metric("BB", "---", "🪵")
    col4.metric("FX", "---", "🤸‍♀️")
    st.info("Waiting for live meet data...")

# --- AZALEA (Level 4 - Purple) ---
with tabs[1]:
    st.markdown('<h2 class="azalea-header">Azalea - Level 4</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("VT", "---", "🏃‍♀️")
    col2.metric("UB", "---", "⚖️")
    col3.metric("BB", "---", "🪵")
    col4.metric("FX", "---", "🤸‍♀️")
    st.info("Waiting for live meet data...")

# --- ANSEL (Level 4 - Teal) ---
with tabs[2]:
    st.markdown('<h2 class="ansel-header">Ansel - Level 4 (Mens)</h2>', unsafe_allow_html=True)
    # Men's 6 Events
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col4, m_col5, m_col6 = st.columns(3)
    m_col1.metric("FX", "---", "🤸‍♂️")
    m_col2.metric("PH", "---", "🐎")
    m_col3.metric("SR", "---", "⭕")
    m_col4.metric("VT", "---", "🏃‍♂️")
    m_col5.metric("PB", "---", "⏸️")
    m_col6.metric("HB", "---", "💈")
    st.info("Waiting for live meet data...")

# --- TEAM OVERVIEW ---
with tabs[3]:
    st.header("Bayshore Elite Insights")
    st.write("Team standings and session averages will appear here.")
