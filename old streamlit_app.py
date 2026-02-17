import streamlit as st
import pandas as pd

# Page setup for mobile optimization
st.set_page_config(page_title="SheehyAllAround", layout="centered")

# Custom Styles
st.markdown("""
    <style>
    .annabelle-txt { color: #FF69B4; font-weight: bold; }
    .azalea-txt { color: #9370DB; font-weight: bold; }
    .ansel-txt { color: #008080; font-weight: bold; }
    .metric-label { font-size: 0.8em; color: #666; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤸‍♂️ Sheehy All-Around")

# Creating the 5 Tabs
t1, t2, t3, t4, t5 = st.tabs(["Annabelle", "Azalea", "Ansel", "BSE Men's", "Bayshore Elite"])

# --- TAB 1: ANNABELLE (L3 Women's) ---
with t1:
    st.markdown('<h2 class="annabelle-txt">Annabelle - Level 3</h2>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VT", "---", "🏃‍♀️")
    c2.metric("UB", "---", "⚖️")
    c3.metric("BB", "---", "🪵")
    c4.metric("FX", "---", "🤸‍♀️")
    st.progress(0, text="Season PB Progress (AA)")

# --- TAB 2: AZALEA (L4 Women's) ---
with t2:
    st.markdown('<h2 class="azalea-txt">Azalea - Level 4</h2>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VT", "---", "🏃‍♀️")
    c2.metric("UB", "---", "⚖️")
    c3.metric("BB", "---", "🪵")
    c4.metric("FX", "---", "🤸‍♀️")
    st.progress(0, text="Season PB Progress (AA)")

# --- TAB 3: ANSEL (L4 Men's) ---
with t3:
    st.markdown('<h2 class="ansel-txt">Ansel - Level 4 (Mens)</h2>', unsafe_allow_html=True)
    row1 = st.columns(3)
    row2 = st.columns(3)
    row1[0].metric("FX", "---", "🤸‍♂️")
    row1[1].metric("PH", "---", "🐎")
    row1[2].metric("SR", "---", "⭕")
    row2[0].metric("VT", "---", "🏃‍♂️")
    row2[1].metric("PB", "---", "⏸️")
    row2[2].metric("HB", "---", "💈")

# --- TAB 4: BSE MEN'S TEAM ---
with t4:
    st.header("BSE Men's Team Results")
    st.caption("Tracking session averages and team rank for the Boys program.")
    st.info("Live data will populate here during Ansel's meets.")

# --- TAB 5: BAYSHORE ELITE TEAM ---
with t5:
    st.header("Bayshore Elite Team Results")
    st.caption("Tracking session averages and team rank for the Girls program.")
    st.info("Live data will populate here during Annabelle or Azalea's meets.")
