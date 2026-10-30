"""Rwanda Crop Timing Advisor - Main Application Router.

Premium Rwanda Dark Mode SaaS aesthetic with native dark theme lock.
"""
import json
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st

from components import state_manager, tab_assistant, tab_expert

DATA = Path(__file__).parent / "data"
PROC = DATA / "processed"

st.set_page_config(
    page_title="Rwanda Crop Timing Advisor",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------- Premium Dark Mode CSS Engine
st.html(
    dedent(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

    :root {
        /* Premium Rwandan Midnight Theme Tokens */
        --bg-canvas: #0B1120;
        --bg-surface: #151E32;
        --border-color: rgba(255, 255, 255, 0.08);
        --text-primary: #F8FAFC;
        --text-secondary: #94A3B8;
        --accent-emerald: #10B981;
        --accent-gold: #FBBF24;
        --accent-blue: #0EA5E9;
        
        --font-mono: 'JetBrains Mono', monospace;
        --font-sans: 'Inter', -apple-system, sans-serif;
        --font-display: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background-color: var(--bg-canvas) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 1400px !important;
    }

    /* Native Container Styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 1.25rem !important;
        box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.25) !important;
        margin-bottom: 0.75rem !important;
    }

    /* Premium SaaS Metric Cards */
    div[data-testid="stMetric"] {
        background-color: var(--bg-canvas) !important;
        border: 1px solid var(--border-color) !important;
        border-top: 3px solid var(--accent-emerald) !important;
        border-radius: 6px !important;
        padding: 1rem 1.25rem !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 6px -1px rgba(0,0,0,0.1) !important;
    }
    div[data-testid="stMetricLabel"] p {
        color: var(--text-secondary) !important;
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    div[data-testid="stMetricValue"] div {
        color: var(--text-primary) !important;
        font-family: var(--font-display) !important;
        font-size: 1.6rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }
    div[data-testid="stMetricDelta"] svg {
        display: none !important;
    }
    div[data-testid="stMetricDelta"] div {
        color: var(--accent-emerald) !important;
        background-color: rgba(16, 185, 129, 0.1) !important;
        padding: 0.15rem 0.5rem !important;
        border-radius: 4px !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        margin-top: 0.25rem !important;
    }

    /* Sidebar Navigation Overrides */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-surface) !important;
        border-right: 1px solid var(--border-color) !important;
    }
    
    label[data-testid="stWidgetLabel"] p {
        font-family: var(--font-mono) !important;
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em;
    }
    div[data-baseweb="select"] > div {
        background-color: var(--bg-canvas) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    div[data-baseweb="popover"] {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-color) !important;
    }
    
    /* Headers & Markdown */
    h1, h2, h3, h4 {
        font-family: var(--font-display) !important;
        color: var(--text-primary) !important;
    }
    p, span {
        color: var(--text-primary);
    }
    .st-emotion-cache-1wivap2 {
        color: var(--text-secondary);
    }
    hr {
        border-color: var(--border-color) !important;
    }
    </style>
        """
    ),
)

@st.cache_data
def load_json(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)

calendar = load_json(PROC / "harvest_calendar.json")
windows = load_json(PROC / "harvest_windows.json")
seasonal = load_json(PROC / "seasonal_price_index.json")
district = load_json(PROC / "district_crop.json")
forecast = load_json(PROC / "price_forecast.json")
geo = load_json(DATA / "districts.geojson")

if calendar is None:
    st.error("Missing data/processed/harvest_calendar.json")
    st.stop()

cal = pd.DataFrame(calendar)

state_manager.init_state(cal)

# ---------------------------------------------------------------- Sidebar Navigation
with st.sidebar:
    st.markdown(
        """
        <div style="margin-bottom: 2rem;">
            <div style="font-family: var(--font-mono); font-size: 0.7rem; font-weight: 700; color: var(--accent-emerald); letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;">
                Intelligence
            </div>
            <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary); line-height: 1.2; font-family: var(--font-display);">
                Rwanda Crop Timing
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    active_view = st.radio(
        "Select View",
        [
            "Farmer Assistant",
            "Crop Explorer",
            "Compare Crops",
            "District Map",
            "Price Outlook"
        ],
        label_visibility="collapsed"
    )

    st.markdown(
        """
        <div style="margin-top: 3rem; border-top: 1px solid var(--border-color); padding-top: 1.5rem;">
            <div style="font-family: var(--font-mono); font-size: 0.65rem; font-weight: 700; color: var(--text-secondary); letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 0.5rem;">
                Data Sources
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 0.25rem;">
                • NISR AHS (2024)
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5;">
                • CPI (to Sep 2026)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------------- Direct Canvas Rendering
if active_view == "Farmer Assistant":
    tab_assistant.render(cal, district)
elif active_view == "Crop Explorer":
    tab_expert.render_crop_explorer(cal, windows, seasonal)
elif active_view == "Compare Crops":
    tab_expert.render_compare_crops(cal)
elif active_view == "District Map":
    tab_expert.render_district_map(cal, district, geo)
elif active_view == "Price Outlook":
    tab_expert.render_price_outlook(forecast)