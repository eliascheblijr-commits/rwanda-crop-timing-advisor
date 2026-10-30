"""Rwanda Crop Timing Advisor - main app. Views live in components/."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from components import state_manager, tab_assistant, tab_expert
from components.i18n import LANGS, t
from components.text import data_as_of

DATA = Path(__file__).parent / "data"
PROC = DATA / "processed"

st.set_page_config(page_title="Rwanda Crop Timing Advisor", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
:root {--bg-canvas:#0B1120; --bg-surface:#151E32; --border-color:rgba(255,255,255,0.08); --text-primary:#F8FAFC;
 --text-secondary:#94A3B8; --accent-emerald:#10B981; --font-mono:'JetBrains Mono',monospace;
 --font-sans:'Inter',-apple-system,sans-serif; --font-display:'Plus Jakarta Sans',sans-serif;}
.stApp {background-color:var(--bg-canvas)!important; color:var(--text-primary)!important; font-family:var(--font-sans)!important;}
#MainMenu, footer {visibility:hidden;}
.block-container {padding-top:2rem!important; padding-bottom:4rem!important; max-width:1400px!important;}
div[data-testid="stVerticalBlockBorderWrapper"] {background-color:var(--bg-surface)!important; border:1px solid var(--border-color)!important;
 border-radius:8px!important; padding:1.25rem!important; box-shadow:0 8px 16px -4px rgba(0,0,0,.25)!important; margin-bottom:.75rem!important;}
div[data-testid="stMetric"] {background-color:var(--bg-canvas)!important; border:1px solid var(--border-color)!important;
 border-top:3px solid var(--accent-emerald)!important; border-radius:6px!important; padding:1rem 1.25rem!important;}
div[data-testid="stMetricLabel"] p {color:var(--text-secondary)!important; font-size:.85rem!important; font-weight:600!important;}
div[data-testid="stMetricValue"] div {color:var(--text-primary)!important; font-family:var(--font-display)!important;
 font-size:1.55rem!important; font-weight:800!important; letter-spacing:-.02em!important;}
div[data-testid="stMetricDelta"] svg {display:none!important;}
div[data-testid="stMetricDelta"] div {color:var(--accent-emerald)!important; background-color:rgba(16,185,129,.1)!important;
 padding:.15rem .5rem!important; border-radius:4px!important; font-size:.78rem!important; font-weight:600!important; margin-top:.25rem!important;}
section[data-testid="stSidebar"] {background-color:var(--bg-surface)!important; border-right:1px solid var(--border-color)!important;}
label[data-testid="stWidgetLabel"] p {color:var(--text-secondary)!important; font-weight:600!important; font-size:.85rem!important;}
div[data-baseweb="select"] > div {background-color:var(--bg-canvas)!important; border:1px solid var(--border-color)!important; border-radius:4px!important;}
div[data-baseweb="popover"] {background-color:var(--bg-surface)!important; border:1px solid var(--border-color)!important;}
h1,h2,h3,h4 {font-family:var(--font-display)!important; color:var(--text-primary)!important;}
hr {border-color:var(--border-color)!important;}
</style>
""")


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

VIEWS = list(range(5))
with st.sidebar:
    lang = st.selectbox(t("language", st.session_state.get("lang", "en")), list(LANGS), format_func=LANGS.get, key="lang")
    st.markdown("<div style='margin:1rem 0 1.2rem'><div style='font-size:1.2rem;font-weight:800;font-family:var(--font-display)'>"
                "Rwanda Crop<br>Timing Advisor</div>"
                f"<div style='font-size:.85rem;color:var(--text-secondary);margin-top:.4rem'>{t('tagline', lang)}</div></div>",
                unsafe_allow_html=True)
    view = st.radio("Page", VIEWS, format_func=lambda i: t(f"nav_{i}", lang), label_visibility="collapsed")
    st.markdown(f"""<div style="margin-top:2.5rem;border-top:1px solid var(--border-color);padding-top:1rem;font-size:.8rem;color:var(--text-secondary);line-height:1.6">
      <b>{t('src_title', lang)}</b><br>{t('src_survey', lang)}<br>
      {t('src_prices', lang, d=data_as_of(forecast, lang))}<br><br>{t('disclaimer', lang)}</div>""", unsafe_allow_html=True)

if view == 0:
    tab_assistant.render(cal, district, lang)
else:
    if lang != "en":
        st.info(t("english_only", lang))
    if view == 1:
        tab_expert.render_crop_explorer(cal, windows, seasonal)
    elif view == 2:
        tab_expert.render_compare_crops(cal)
    elif view == 3:
        tab_expert.render_district_map(cal, district, geo)
    else:
        tab_expert.render_price_outlook(forecast)
