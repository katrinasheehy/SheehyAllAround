import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def create_context_chart(row, theme_color="#FF4B4B"):
    """
    Creates the Layered Horizontal Bullet Chart for a gymnastics event.
    """
    fig = go.Figure()

    # Layer 1: Session Range (The full competitive field)
    fig.add_trace(go.Bar(
        y=["Score"], 
        x=[row['Session_Max'] - 7.0], 
        base=7.0,
        orientation='h', 
        marker_color='#E0E0E0', 
        name='Full Session Range',
        hoverinfo='skip', 
        width=0.5
    ))

    # Layer 2: Division Range (The age group specific field)
    # If Division_Max isn't in your CSV, it falls back to Session_Max
    div_max = row.get('Division_Max', row['Session_Max'])
    fig.add_trace(go.Bar(
        y=["Score"], 
        x=[div_max - 7.0], 
        base=7.0,
        orientation='h', 
        marker_color=theme_color, 
        name='Age Division Range',
        width=0.3
    ))

    # Marker 1: The Child's Score (The Gold Star)
    fig.add_trace(go.Scatter(
        x=[row['Score']], 
        y=["Score"], 
        mode='markers',
        marker=dict(symbol='star', size=18, color='gold', line=dict(width=2, color='DarkSlateGrey')),
        name='Score'
    ))

    # Marker 2: The Division Median (The White Line)
    fig.add_trace(go.Scatter(
        x=[row['Session_Median']], 
        y=["Score"], 
        mode='markers',
        marker=dict(symbol='line-ns-open', size=25, color='white', line=dict(width=3)),
        name='Median'
    ))

    # Clean up the visual appearance
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False, 
        margin=dict(l=0, r=0, t=0, b=0),
        height=120, 
        xaxis=dict(range=[7.0, 10.0], showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False)
    )
    return fig

def show_athlete_history(gymnast_name):
    """
    Renders the meet history and the interactive context cards for a child.
    """
    # Load the analytics data we generated
    try:
        df = pd.read_csv("session_context_analytics.csv")
    except FileNotFoundError:
        st.error("Missing 'session_context_analytics.csv'. Please ensure the file is in your folder.")
        return

    # Filter for the specific child
    # Note: We use a 'contains' check to handle names like 'Ansel Sheehy'
    child_data = df[df['Gymnast'].str.contains(gymnast_name.split()[0], case=False)].copy()
    
    if child_data.empty:
        st.warning(f"No 2026 data found for {gymnast_name}.")
        return

    # 1. Navigation: Select Meet
    all_meets = child_data['Meet'].unique()
    selected_meet = st.selectbox("📅 Which meet would you like to explore?", all_meets)
    
    meet_rows = child_data[child_data['Meet'] == selected_meet]
    
    # 2. Judge Weather Indicator
    avg_jsi = meet_rows['JSI'].mean()
    if avg_jsi <= -0.15:
        st.error(f"🌬️ **Judge Mood:** Significantly Stricter than Average (JSI: {avg_jsi:.2f})")
    elif avg_jsi >= 0.15:
        st.success(f"☀️ **Judge Mood:** Significantly Looser than Average (JSI: {avg_jsi:.2f})")
    else:
        st.info(f"☁️ **Judge Mood:** Typical Scoring Environment (JSI: {avg_jsi:.2f})")

    # 3. Build the Grid of Cards
    # On an iPhone, this will stack vertically
    for idx, (index, row) in enumerate(meet_rows.iterrows()):
        state_key = f"flip_{gymnast_name}_{selected_meet}_{row['Event']}"
        if state_key not in st.session_state:
            st.session_state[state_key] = False
            
        with st.container(border=True):
            if not st.session_state[state_key]:
                # FRONT OF CARD
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.subheader(row['Event'])
                with c2:
                    st.button("Context 🔍", key=f"btn_{state_key}", on_click=lambda k=state_key: st.session_state.update({k: True}))
                
                st.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>{row['Score']:.3f}</h1>", unsafe_allow_name=True)
            else:
                # BACK OF CARD (The Analysis)
                st.subheader(f"{row['Event']} Performance Analysis")
                
                # Show the chart
                chart = create_context_chart(row)
                st.plotly_chart(chart, use_container_width=True, config={'displayModeBar': False})
                
                # The Insight Sentence
                st.write(f"**Insight:** Beating **{row['Percentile']:.0f}%** of the field.")
                st.caption(f"Context: Session of {int(row['Count'])} Level {row['Level']} athletes.")
                
                st.button("Back to Score", key=f"back_{state_key}", on_click=lambda k=state_key: st.session_state.update({k: False}))
