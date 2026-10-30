"""Rwanda Crop Timing Advisor - Streamlit app.

Four tabs: crop explorer, compare crops, district map, price outlook.
All data is read from pre-computed files in data/ (see scripts/ for how they are built).
"""
import json
from pathlib import Path
from textwrap import dedent

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / "data"
PROC = DATA / "processed"

st.set_page_config(
    page_title="Rwanda Crop Timing Advisor",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------- Mobile-First App UI & Phosphor Icons Engine
st.html(
    dedent(
        """
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/regular/style.css" />
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/bold/style.css" />
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

    /* Force crisp high-contrast light surface regardless of device dark/light theme */
    .stApp {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 4rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 1280px !important;
    }
    @media (min-width: 768px) {
        .block-container {
            padding-top: 1.5rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }
    }

    /* Phosphor Icon Alignment Helpers */
    .ph, .ph-bold {
        vertical-align: middle;
        line-height: 1;
    }

    /* App Shell Header */
    .app-shell-header {
        background: linear-gradient(135deg, #0b2419 0%, #14532d 100%);
        border: 1.5px solid #0f172a;
        border-radius: 14px;
        padding: 1.25rem 1.25rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.75rem;
    }
    @media (min-width: 768px) {
        .app-shell-header {
            padding: 1.5rem 2rem;
        }
    }
    .app-brand-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #86efac !important;
        margin-bottom: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .app-main-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #ffffff !important;
        font-size: 1.45rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0 0 0.25rem 0;
        line-height: 1.2;
    }
    @media (min-width: 768px) {
        .app-main-title {
            font-size: 1.85rem;
        }
    }
    .app-main-sub {
        color: #e2e8f0 !important;
        font-size: 0.85rem;
        line-height: 1.45;
        margin: 0;
        max-width: 680px;
    }
    .app-source-pills {
        display: flex;
        gap: 0.45rem;
        flex-wrap: wrap;
    }
    .source-pill {
        background-color: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.25);
        color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.32rem 0.65rem;
        border-radius: 999px;
        white-space: nowrap;
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Sticky Touch-Friendly Segmented App Navigation Bar */
    div[data-testid="stTabs"] > div:first-child {
        position: sticky;
        top: 0;
        z-index: 99;
        background-color: rgba(241, 245, 249, 0.95);
        backdrop-filter: blur(8px);
        padding: 0.35rem 0 0.65rem 0;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-list"] {
        background-color: #ffffff !important;
        padding: 0.3rem !important;
        border-radius: 12px !important;
        border: 1.5px solid #cbd5e1 !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.06) !important;
        gap: 0.25rem !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        scrollbar-width: none !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        flex: 1 1 auto !important;
        min-height: 44px !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 0.95rem !important;
        color: #334155 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        white-space: nowrap !important;
        transition: all 0.15s ease !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.45rem !important;
    }
    /* Phosphor Icons injected cleanly via CSS on native Streamlit tab buttons */
    div[data-testid="stTabs"] button[data-baseweb="tab"]::before {
        font-family: "Phosphor-Bold" !important;
        font-size: 1.05rem;
        font-weight: normal;
        font-style: normal;
        line-height: 1;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"]:nth-child(1)::before {
        content: "\\e3d2"; /* ph-bold ph-plant */
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"]:nth-child(2)::before {
        content: "\\e418"; /* ph-bold ph-scales */
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"]:nth-child(3)::before {
        content: "\\e31c"; /* ph-bold ph-map-trifold */
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"]:nth-child(4)::before {
        content: "\\e14e"; /* ph-bold ph-chart-line-up */
    }

    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        background-color: #f1f5f9 !important;
        color: #0f172a !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #14532d !important;
        color: #ffffff !important;
        box-shadow: 0 2px 5px rgba(20, 83, 45, 0.25) !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p,
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"]::before {
        color: #ffffff !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Card Containers */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        margin-bottom: 0.65rem !important;
    }
    @media (min-width: 768px) {
        div[data-testid="stVerticalBlockBorderWrapper"] {
            padding: 1.25rem !important;
        }
    }

    /* Everyday User "Quick Takeaway" Insight Banner */
    .takeaway-banner {
        background-color: #ffffff;
        border: 1.5px solid #14532d;
        border-left: 6px solid #15803d;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.05);
    }
    .takeaway-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #15803d !important;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .takeaway-label i {
        font-size: 1rem;
    }
    .takeaway-text {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.96rem;
        font-weight: 600;
        color: #0f172a !important;
        line-height: 1.5;
        margin: 0;
    }
    .takeaway-highlight {
        background-color: #dcfce7;
        color: #14532d !important;
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        font-weight: 700;
    }
    .takeaway-warn {
        background-color: #ffedd5;
        color: #9a3412 !important;
        padding: 0.1rem 0.4rem;
        border-radius: 4px;
        font-weight: 700;
    }

    /* Responsive App Data Cards */
    .data-card-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    @media (min-width: 640px) {
        .data-card-grid {
            grid-template-columns: repeat(3, 1fr);
            gap: 0.9rem;
        }
    }
    .data-card {
        background-color: #ffffff;
        border: 1.5px solid #cbd5e1;
        border-radius: 12px;
        padding: 1rem 1.1rem;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .data-card.top-emerald { border-top: 4px solid #15803d; }
    .data-card.top-amber { border-top: 4px solid #c2410c; }
    .data-card.top-slate { border-top: 4px solid #0f172a; }

    .dc-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.4rem;
    }
    .dc-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: #334155 !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .dc-icon {
        width: 28px;
        height: 28px;
        border-radius: 6px;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #0f172a !important;
        font-size: 0.95rem;
        flex-shrink: 0;
    }
    .dc-value {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a !important;
        letter-spacing: -0.02em;
        line-height: 1.2;
        margin-bottom: 0.45rem;
    }
    .dc-value.mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.45rem;
    }
    .dc-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        width: fit-content;
        margin-bottom: 0.4rem;
    }
    .pill-green { background-color: #dcfce7; color: #14532d !important; border: 1px solid #86efac; }
    .pill-amber { background-color: #ffedd5; color: #7c2d12 !important; border: 1px solid #fdba74; }
    .pill-slate { background-color: #f1f5f9; color: #1e293b !important; border: 1px solid #cbd5e1; }

    .dc-helper {
        font-size: 0.76rem;
        color: #475569 !important;
        line-height: 1.35;
        margin-top: auto;
        padding-top: 0.4rem;
        border-top: 1px dashed #e2e8f0;
    }

    /* Section Headers Inside Cards */
    .card-section-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.4rem;
        border-bottom: 1.5px solid #f1f5f9;
        padding-bottom: 0.6rem;
        margin-bottom: 0.75rem;
    }
    .card-section-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.98rem;
        font-weight: 800;
        color: #0f172a !important;
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
    }
    .card-section-title i {
        color: #15803d !important;
        font-size: 1.1rem;
    }
    .card-section-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        color: #1e293b !important;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 0.18rem 0.55rem;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    .card-plain-explainer {
        font-size: 0.84rem;
        color: #334155 !important;
        line-height: 1.45;
        margin-bottom: 0.75rem;
    }

    /* Form Controls Contrast & Touch Sizing */
    label[data-testid="stWidgetLabel"] p {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 0.84rem !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border: 1.5px solid #94a3b8 !important;
        border-radius: 8px !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        min-height: 42px !important;
    }

    /* Expander Styling with Phosphor Icon for Technical Notes */
    div[data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        margin-top: 0.75rem !important;
    }
    div[data-testid="stExpander"] summary p {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        color: #1e293b !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.45rem !important;
    }
    div[data-testid="stExpander"] summary p::before {
        font-family: "Phosphor-Bold" !important;
        content: "\\e2ce"; /* ph-bold ph-info */
        font-size: 1rem;
        color: #15803d;
        font-weight: normal;
    }
    .tech-note-body {
        font-size: 0.82rem;
        color: #334155 !important;
        line-height: 1.6;
    }
    .tech-note-item {
        display: flex;
        align-items: flex-start;
        gap: 0.5rem;
        margin-bottom: 0.35rem;
    }
    .tech-note-item i {
        color: #15803d !important;
        margin-top: 0.2rem;
        flex-shrink: 0;
    }
    </style>
        """
    ),
)


def render_data_card(
    title,
    value,
    pill_text="",
    pill_tone="slate",
    helper="",
    accent="emerald",
    is_mono=False,
    icon="ph-chart-bar",
):
    """Renders a mobile-responsive card with a Phosphor icon, technical readout, and plain-English helper."""
    val_cls = "dc-value mono" if is_mono else "dc-value"
    pill_html = f'<div class="dc-pill pill-{pill_tone}">{pill_text}</div>' if pill_text else ""
    helper_html = f'<div class="dc-helper">{helper}</div>' if helper else ""
    return (
        f'<div class="data-card top-{accent}">'
        f'<div>'
        f'<div class="dc-header">'
        f'<span class="dc-title">{title}</span>'
        f'<span class="dc-icon"><i class="ph-bold {icon}"></i></span>'
        f'</div>'
        f'<div class="{val_cls}">{value}</div>'
        f'{pill_html}'
        f'</div>'
        f'{helper_html}'
        f'</div>'
    )


PLOTLY_FONT = dict(family="Inter, -apple-system, sans-serif", color="#0f172a", size=12)
AXIS_STYLE = dict(
    tickfont=dict(family="JetBrains Mono, monospace", color="#0f172a", size=11),
    title_font=dict(family="Plus Jakarta Sans, sans-serif", color="#0f172a", size=12),
    gridcolor="#e2e8f0",
    linecolor="#cbd5e1",
    linewidth=1,
    zerolinecolor="#94a3b8",
    fixedrange=True,  # Prevents touch scroll traps on mobile devices
)
TOUCH_SAFE_CONFIG = {"displayModeBar": False, "responsive": True}


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

# ---------------------------------------------------------------- App Header
st.markdown(
    """
    <div class="app-shell-header">
        <div>
            <div class="app-brand-tag"><i class="ph-bold ph-grains"></i> RWANDA AGRICULTURAL INTELLIGENCE</div>
            <h1 class="app-main-title">Rwanda Crop Timing Advisor</h1>
            <p class="app-main-sub">
                When crops are harvested, where they are grown, and how food prices behave.
                NISR Agricultural Household Survey 2024 &amp; Consumer Price Index to September 2026.
            </p>
        </div>
        <div class="app-source-pills">
            <span class="source-pill"><i class="ph-bold ph-database"></i> NISR AHS 2024</span>
            <span class="source-pill"><i class="ph-bold ph-trend-up"></i> CPI Sep 2026</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4 = st.tabs([
    "Crop Explorer",
    "Compare Crops",
    "District Map",
    "Price Outlook",
])

# ---------------------------------------------------------------- 1. crop explorer
with tab1:
    # Filter Selector Bar
    with st.container(border=True):
        c_a, c_b = st.columns(2)
        crop = c_a.selectbox("Select Crop", sorted(cal["crop"].unique()), key="ex_crop")
        seasons = sorted(cal.loc[cal["crop"] == crop, "season"].unique())
        season = c_b.selectbox("Select Season", seasons, key="ex_season")

    row = cal[(cal["crop"] == crop) & (cal["season"] == season)].iloc[0]

    # Everyday User Plain-English "Quick Takeaway" Banner
    sowing_str = row["peak_sowing_window"] if pd.notna(row["peak_sowing_window"]) else "an unspecified window"
    if pd.notna(row.get("price_gain_hold_3m_pct")):
        price_timing_desc = (
            '<span class="takeaway-warn">cheaper than the yearly average</span>'
            if row["harvest_in_cheap_season"]
            else '<span class="takeaway-highlight">around or above the yearly average</span>'
        )
        if row["price_gain_hold_3m_pct"] > 0:
            hold_advice = (
                f"Historically, waiting up to 3 months until <strong>{row['best_month_within_3m'][3:]}</strong> "
                f"saw consumer prices rise by <span class='takeaway-highlight'>+{row['price_gain_hold_3m_pct']:.1f}%</span>."
            )
        else:
            hold_advice = "Historically, the harvest month itself already offers the best price within a 3-month window."
    else:
        price_timing_desc = "not tracked by a specific CPI food group"
        hold_advice = ""

    st.markdown(
        f'<div class="takeaway-banner">'
        f'<div class="takeaway-label"><i class="ph-bold ph-lightbulb"></i> Plain-English Summary // {crop} ({season})</div>'
        f'<p class="takeaway-text">'
        f'Farmers most commonly plant in <strong>{sowing_str}</strong> and harvest in '
        f'<span class="takeaway-highlight">{row["peak_harvest_window"]}</span>. '
        f'At harvest time, market prices are typically {price_timing_desc}. {hold_advice}'
        f'</p></div>',
        unsafe_allow_html=True,
    )

    # Agronomic Data Cards (Everyday + Technical Dual Layer)
    sowing_val = row["peak_sowing_window"] if pd.notna(row["peak_sowing_window"]) else "n/a"
    if pd.notna(row["yield_kg_per_ha_median"]):
        yield_val = f"{int(row['yield_kg_per_ha_median']):,}"
        yield_pill = f"middle half: {int(row['yield_kg_per_ha_p25']):,} to {int(row['yield_kg_per_ha_p75']):,}"
    else:
        yield_val = "n/a"
        yield_pill = "No median available"

    st.markdown(
        '<div class="data-card-grid">'
        + render_data_card(
            "Most common harvest window",
            row["peak_harvest_window"],
            pill_text=f"{row['peak_window_share']:.0%} of plots with a stated window",
            pill_tone="green",
            helper="Peak period when the largest share of surveyed farmers gather this crop.",
            accent="emerald",
            icon="ph-calendar-check",
        )
        + render_data_card(
            "Most common sowing window",
            sowing_val,
            pill_text="Primary planting window",
            pill_tone="slate",
            helper="Most frequent planting timeframe reported for this season.",
            accent="slate",
            icon="ph-seedling",
        )
        + render_data_card(
            "Median yield (kg/ha)",
            yield_val,
            pill_text=yield_pill,
            pill_tone="amber",
            helper="Typical harvest output per hectare (50% of farms fall in the middle half).",
            accent="amber",
            is_mono=True,
            icon="ph-scales",
        )
        + "</div>",
        unsafe_allow_html=True,
    )

    if row["share_window_unspecified"] > 0.2:
        st.warning(f"{row['share_window_unspecified']:.0%} of {crop} records have no specific harvest window "
                   "(typical for perennial or year-round crops), so the pattern below covers only the rest.")

    # Responsive Split: Stacks cleanly on mobile, side-by-side on desktop
    col_harvest, col_price = st.columns([1, 1.1], gap="medium")

    with col_harvest:
        if windows:
            w = pd.DataFrame(windows)
            w = w[(w["crop"] == crop) & (w["season"] == season)].sort_values("order")
            w = w.assign(label=w["order"].astype(str) + ". " + w["window"])  # numbered so labels stay in time order
            with st.container(border=True):
                st.markdown(
                    '<div class="card-section-head">'
                    '<span class="card-section-title"><i class="ph-bold ph-chart-bar"></i> When the harvest happens</span>'
                    '<span class="card-section-badge"><i class="ph-bold ph-Percent"></i> Share of plots</span>'
                    '</div>'
                    '<div class="card-plain-explainer">'
                    'Taller green bars show when most farmers bring their crop to market (high supply).'
                    '</div>',
                    unsafe_allow_html=True,
                )
                peak_s = w["share"].max() if not w.empty else 0
                b_colors = ["#15803d" if val == peak_s and peak_s > 0 else "#475569" for val in w["share"]]
                wf = go.Figure(
                    go.Bar(
                        x=w["label"],
                        y=w["share"],
                        marker=dict(color=b_colors, cornerradius=4),
                        text=(w["share"] * 100).round(0).astype(int).astype(str) + "%",
                        textposition="outside",
                        textfont=dict(family="JetBrains Mono, monospace", color="#0f172a", size=10),
                        cliponaxis=False,
                        hovertemplate="<b>%{x}</b><br>Share of plots: %{y:.1%}<extra></extra>",
                    )
                )
                wf.update_layout(
                    height=300,
                    margin=dict(l=4, r=4, t=22, b=8),
                    font=PLOTLY_FONT,
                    xaxis=dict(**AXIS_STYLE, title=None, tickangle=-30),
                    yaxis=dict(
                        **AXIS_STYLE,
                        title=None,
                        tickformat=".0%",
                        range=[0, max(peak_s * 1.25, 0.1)],
                    ),
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                )
                st.plotly_chart(wf, width="stretch", config=TOUCH_SAFE_CONFIG)

    with col_price:
        group = row["cpi_group"]
        with st.container(border=True):
            st.markdown(
                f'<div class="card-section-head">'
                f'<span class="card-section-title"><i class="ph-bold ph-chart-line"></i> Typical consumer price pattern</span>'
                f'<span class="card-section-badge"><i class="ph-bold ph-tag"></i> CPI Group: {group if group else "N/A"}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if seasonal and group and group in seasonal:
                st.markdown(
                    '<div class="card-plain-explainer">'
                    '<strong>How to read this:</strong> 1.00 is the yearly average price. Below 1.00 means cheaper '
                    'than usual; above 1.00 means more expensive. The <strong style="color:#c2410c;">orange dot</strong> '
                    'marks the main harvest month.'
                    '</div>',
                    unsafe_allow_html=True,
                )
                s_idx = pd.Series(seasonal[group])
                xl = [k[3:] for k in s_idx.index]
                pf = go.Figure(
                    go.Scatter(
                        x=xl,
                        y=s_idx.values,
                        mode="lines+markers",
                        name="Seasonal price index",
                        line=dict(color="#15803d", width=3),
                        marker=dict(size=6, color="#15803d"),
                        fill="tozeroy",
                        fillcolor="rgba(21, 128, 61, 0.08)",
                    )
                )
                if pd.notna(row.get("peak_approx_month")):
                    hm = int(row["peak_approx_month"]) - 1
                    pf.add_trace(
                        go.Scatter(
                            x=[xl[hm]],
                            y=[s_idx.values[hm]],
                            mode="markers",
                            name="Harvest month",
                            marker=dict(size=14, color="#c2410c", line=dict(color="#ffffff", width=2)),
                        )
                    )
                pf.add_hline(y=1.0, line_dash="dot", line_color="#475569")
                pf.update_layout(
                    height=280,
                    margin=dict(l=4, r=4, t=10, b=8),
                    font=PLOTLY_FONT,
                    hovermode="x unified",
                    legend=dict(orientation="h", y=-0.22, font=dict(color="#0f172a", size=11)),
                    xaxis=dict(**AXIS_STYLE),
                    yaxis=dict(
                        **AXIS_STYLE,
                        title="Index (1.0 = avg)",
                        range=[min(s_idx.min(), 0.97) - 0.02, max(s_idx.max(), 1.03) + 0.02],
                    ),
                    paper_bgcolor="#ffffff",
                    plot_bgcolor="#ffffff",
                )
                st.plotly_chart(pf, width="stretch", config=TOUCH_SAFE_CONFIG)
                if row["cpi_mapping_confidence"] == "probable_verify":
                    st.warning(f"{crop} is assumed to follow the '{group}' price group. This mapping is unverified.")
            else:
                st.info("Price pattern not available for this crop (no matching CPI food group).")

    # Price Timing & Storage Gain Cards
    if seasonal and group and group in seasonal and pd.notna(row.get("price_gain_hold_3m_pct")):
        p_tone = "green" if row["harvest_in_cheap_season"] else "slate"
        p_text = "cheaper than average" if row["harvest_in_cheap_season"] else "about average or higher"
        if row["price_gain_hold_3m_pct"] > 0:
            m3_pill = f"+{row['price_gain_hold_3m_pct']:.1f}% vs harvest month"
            m3_tone = "green"
        else:
            m3_pill = "harvest month is already the best"
            m3_tone = "slate"

        st.markdown(
            '<div class="data-card-grid">'
            + render_data_card(
                "Price index at harvest",
                f"{row['price_index_at_harvest']:.3f}",
                pill_text=p_text,
                pill_tone=p_tone,
                helper="1.000 is the annual average. Values below 1.000 indicate a post-harvest price dip.",
                accent="slate",
                is_mono=True,
                icon="ph-tag",
            )
            + render_data_card(
                "Best month within 3 months",
                row["best_month_within_3m"][3:],
                pill_text=m3_pill,
                pill_tone=m3_tone,
                helper="Highest-priced month if holding produce up to 3 months after peak harvest.",
                accent="emerald",
                icon="ph-clock-countdown",
            )
            + render_data_card(
                "Best gain within 6 months",
                f"+{row['price_gain_hold_6m_pct']:.1f}%",
                pill_text="Max 6-month seasonal gain",
                pill_tone="amber",
                helper="Gross consumer price rise before accounting for storage costs or spoilage.",
                accent="amber",
                is_mono=True,
                icon="ph-trend-up",
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    with st.expander("Technical Methodology & Sample Details (For Analysts)"):
        st.markdown(
            f'<div class="tech-note-body">'
            f'<div class="tech-note-item"><i class="ph-bold ph-database"></i>'
            f'<span><strong>Sample Size:</strong> Based on <strong>{int(row["n_entries"]):,}</strong> survey records, '
            f'unweighted. One survey year: descriptive, not a forecast.</span></div>'
            f'<div class="tech-note-item"><i class="ph-bold ph-stack"></i>'
            f'<span><strong>CPI Grouping ({group}):</strong> All crops in a group share the same price pattern; '
            f'crops differ only through their harvest timing.</span></div>'
            f'<div class="tech-note-item"><i class="ph-bold ph-warning-circle"></i>'
            f'<span><strong>Price Definition:</strong> Consumer price index, not farm-gate price. The gain ignores '
            f'storage costs and post-harvest losses, which the survey does not measure.</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------- 2. compare crops
with tab2:
    with st.container(border=True):
        st.markdown(
            '<div class="card-section-head">'
            '<span class="card-section-title"><i class="ph-bold ph-scales"></i> Which crops are harvested when prices are low, and gain most from waiting?</span>'
            '<span class="card-section-badge"><i class="ph-bold ph-Sliders-horizontal"></i> Season Comparison</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        k1, k2 = st.columns([1, 2])
        season2 = k1.selectbox("Season", sorted(cal["season"].unique()), key="cmp_season")
        METRICS = {
            "Price gain from holding up to 3 months (%)": ("price_gain_hold_3m_pct", False),
            "Best price gain within 6 months (%)": ("price_gain_hold_6m_pct", False),
            "Price index at harvest (lowest = harvested when prices are cheapest)": ("price_index_at_harvest", True),
        }
        metric_name = k2.selectbox("Rank by", list(METRICS))
        col, ascending = METRICS[metric_name]
        only_verified = st.checkbox("Only crops whose price group is not an assumption", value=False)

    d = cal[(cal["season"] == season2) & cal[col].notna()].copy()
    if only_verified:
        d = d[d["cpi_mapping_confidence"] == "assumed"]
    if d.empty:
        st.info("No crops with a price pattern match these filters.")
    else:
        d = d.sort_values(col, ascending=ascending)
        d["rank"] = d[col].rank(method="min", ascending=ascending).astype(int)

        top_crop = d.iloc[0]
        st.markdown(
            f'<div class="takeaway-banner">'
            f'<div class="takeaway-label"><i class="ph-bold ph-trophy"></i> Top Ranked in {season2} // {metric_name}</div>'
            f'<p class="takeaway-text">'
            f'<strong>{top_crop["crop"]}</strong> ranks #1 for this metric '
            f'(<span class="takeaway-highlight">{top_crop[col]:.2f}</span>), with its main harvest occurring in '
            f'<strong>{top_crop["peak_harvest_window"]}</strong>.'
            f'</p></div>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown(
                f'<div class="card-section-head">'
                f'<span class="card-section-title"><i class="ph-bold ph-chart-bar-horizontal"></i> Visual Ranking ({season2})</span>'
                f'<span class="card-section-badge"><i class="ph-bold ph-list-numbers"></i> {len(d)} Crops Compared</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            bar_colors2 = ["#15803d" if r <= 3 else "#475569" for r in d["rank"]]
            fig = go.Figure(
                go.Bar(
                    x=d[col],
                    y=d["crop"],
                    orientation="h",
                    marker=dict(color=bar_colors2, cornerradius=4),
                    text=d[col].round(2),
                    textposition="outside",
                    textfont=dict(family="JetBrains Mono, monospace", color="#0f172a", size=11),
                    cliponaxis=False,
                )
            )
            fig.update_yaxes(autorange="reversed", **AXIS_STYLE)
            fig.update_xaxes(**AXIS_STYLE, title=metric_name)
            fig.update_layout(
                height=max(280, 28 * len(d) + 70),
                margin=dict(l=4, r=45, t=10, b=10),
                font=PLOTLY_FONT,
                paper_bgcolor="#ffffff",
                plot_bgcolor="#ffffff",
            )
            st.plotly_chart(fig, width="stretch", config=TOUCH_SAFE_CONFIG)

        show = d[["rank", "crop", "peak_harvest_window", "cpi_group", "price_index_at_harvest", "best_month_within_3m",
                  "price_gain_hold_3m_pct", "price_gain_hold_6m_pct", "yield_kg_per_ha_median",
                  "share_window_unspecified", "cpi_mapping_confidence"]].rename(columns={
            "peak_harvest_window": "peak harvest", "cpi_group": "price group", "price_index_at_harvest": "price index at harvest",
            "best_month_within_3m": "best month (3m)", "price_gain_hold_3m_pct": "gain 3m %", "price_gain_hold_6m_pct": "gain 6m %",
            "yield_kg_per_ha_median": "median yield kg/ha", "share_window_unspecified": "no stated window",
            "cpi_mapping_confidence": "mapping"})
        show["best month (3m)"] = show["best month (3m)"].str[3:]
        show["no stated window"] = (show["no stated window"] * 100).round(0).astype(int).astype(str) + "%"

        with st.container(border=True):
            st.markdown(
                '<div class="card-section-head">'
                '<span class="card-section-title"><i class="ph-bold ph-table"></i> Full Crop Comparison Table</span>'
                '<span class="card-section-badge"><i class="ph-bold ph-arrows-left-right"></i> Swipe horizontally on mobile</span>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(
                show,
                hide_index=True,
                width="stretch",
                column_config={
                    "rank": st.column_config.NumberColumn("Rank", format="#%d", width="small"),
                    "crop": st.column_config.TextColumn("Crop", width="medium"),
                    "price index at harvest": st.column_config.NumberColumn("Harvest CPI", format="%.3f"),
                    "gain 3m %": st.column_config.NumberColumn("Gain (3m)", format="+%.1f%%"),
                    "gain 6m %": st.column_config.NumberColumn("Gain (6m)", format="+%.1f%%"),
                    "median yield kg/ha": st.column_config.NumberColumn("Median Yield", format="%d kg/ha"),
                },
            )

        with st.expander("Technical Methodology & Tie-Breaking Rules"):
            st.markdown(
                '<div class="tech-note-body">'
                '<div class="tech-note-item"><i class="ph-bold ph-git-merge"></i>'
                '<span>Crops in the same price group with the same harvest month tie by construction, because the price '
                'pattern is measured per food group, not per crop.</span></div>'
                '<div class="tech-note-item"><i class="ph-bold ph-warning-circle"></i>'
                '<span>Yields are not comparable across crops. Gains are consumer-price index changes and ignore '
                'storage costs and losses.</span></div>'
                '<div class="tech-note-item"><i class="ph-bold ph-seal-question"></i>'
                '<span>\'assumed\' and \'probable_verify\' mappings are not confirmed against NISR\'s CPI methodology.</span></div>'
                '</div>',
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------- 3. district map
with tab3:
    if district is None or geo is None:
        st.info("District data not available.")
    else:
        dc = pd.DataFrame(district)
        with st.container(border=True):
            st.markdown(
                '<div class="card-section-head">'
                '<span class="card-section-title"><i class="ph-bold ph-map-trifold"></i> Where is each crop grown, and how does yield differ by district?</span>'
                '<span class="card-section-badge"><i class="ph-bold ph-map-pin"></i> 30 Districts</span>'
                '</div>',
                unsafe_allow_html=True,
            )
            q1, q2, q3 = st.columns([1, 1.2, 1.4])
            season3 = q1.selectbox("Season", sorted(dc["season"].unique()), key="map_season")
            crops3 = sorted(dc.loc[dc["season"] == season3, "crop"].unique())
            crop3 = q2.selectbox("Crop", crops3, index=crops3.index("Irish potato") if "Irish potato" in crops3 else 0,
                                 key="map_crop")
            mode = q3.radio("Show on map", ["Share of crop entries (%)", "Median yield (kg/ha)"],
                            horizontal=True, key="map_metric")

        all_d = pd.DataFrame({"district": [f["properties"]["district"] for f in geo["features"]]})
        sub = dc[(dc["season"] == season3) & (dc["crop"] == crop3)]
        m = all_d.merge(sub, on="district", how="left")
        totals = dc[dc["season"] == season3].drop_duplicates("district").set_index("district")["district_total_entries"]
        m["district_total_entries"] = m["district"].map(totals)
        if mode.startswith("Share"):
            m["value"] = m["share_of_entries"] * 100
            m.loc[m["district_total_entries"].fillna(0) < 100, "value"] = None   # too few records in district-season
            unit, label = "%", "share of all crop entries in the district"
        else:
            m["value"] = m["yield_kg_per_ha_median"]                              # already blank where n < 30
            unit, label = " kg/ha", "median yield (needs 30+ records)"
        # a crop that is not recorded in a district has zero share, not "missing"
        if mode.startswith("Share"):
            m.loc[m["share_of_entries"].isna() & (m["district_total_entries"].fillna(0) >= 100), "value"] = 0.0
        has = m.dropna(subset=["value"])
        n_grey = len(m) - len(has)

        if not has.empty:
            lo, hi = has["value"].min(), has["value"].max()
            top_dist_row = has.sort_values("value", ascending=False).iloc[0]
            st.markdown(
                '<div class="data-card-grid">'
                + render_data_card(
                    "Highest District",
                    top_dist_row["district"],
                    pill_text=f"{top_dist_row['value']:,.1f}{unit}",
                    pill_tone="green",
                    helper=f"Leading district for {crop3} ({mode.lower()}) in {season3}.",
                    accent="emerald",
                    icon="ph-Navigation-arrow",
                )
                + render_data_card(
                    "Observed Range",
                    f"{lo:,.1f} – {hi:,.1f}{unit}",
                    pill_text=label,
                    pill_tone="slate",
                    helper="Spread between the lowest and highest reporting districts.",
                    accent="slate",
                    is_mono=True,
                    icon="ph-arrows-out-line-horizontal",
                )
                + render_data_card(
                    "District Coverage",
                    f"{len(has)} of {len(m)}",
                    pill_text=f"{n_grey} in grey (too few records)",
                    pill_tone="amber" if n_grey > 10 else "slate",
                    helper="Districts meeting minimum sample size thresholds.",
                    accent="amber",
                    is_mono=True,
                    icon="ph-grid-four",
                )
                + "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.warning("Not enough survey records in any district for this choice.")

        if season3 == "Season C":
            st.warning("Season C has very few records per district, so most of the map is grey.")

        hover = (m["district"] + "<br>" + m["value"].map(lambda v: "n/a" if pd.isna(v) else f"{v:,.1f}{unit}") +
                 "<br>records: " + m["n_entries"].fillna(0).astype(int).astype(str))
        # MapLibre-based map with a blank background: no tiles or outside files are fetched
        with st.container(border=True):
            st.markdown(
                f'<div class="card-section-head">'
                f'<span class="card-section-title"><i class="ph-bold ph-globe-hemisphere-east"></i> {crop3} ({season3}) — District Choropleth</span>'
                f'<span class="card-section-badge"><i class="ph-bold ph-hand-tap"></i> Tap a district for details</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            fig = go.Figure()
            fig.add_trace(go.Choroplethmap(geojson=geo, featureidkey="properties.district", locations=m["district"],
                                           z=[0] * len(m), colorscale=[[0, "#cbd5e1"], [1, "#cbd5e1"]], showscale=False,
                                           marker_line_color="#ffffff", marker_line_width=1.0, hoverinfo="skip"))
            if not has.empty:
                fig.add_trace(go.Choroplethmap(geojson=geo, featureidkey="properties.district", locations=has["district"],
                                               z=has["value"], colorscale="YlGn", marker_line_color="#0f172a",
                                               marker_line_width=1.0, hovertext=hover[has.index], hoverinfo="text",
                                               colorbar=dict(title=dict(text=unit.strip() or "%"), thickness=12)))
            fig.update_layout(map=dict(style="white-bg", center=dict(lat=-1.95, lon=29.9), zoom=7.3),
                              height=460, margin=dict(l=0, r=0, t=5, b=0), font=PLOTLY_FONT,
                              paper_bgcolor="#ffffff")
            st.plotly_chart(fig, width="stretch", config=TOUCH_SAFE_CONFIG)

        with st.expander("Technical Cartography & Sample Notes"):
            if not has.empty:
                st.markdown(
                    f'<div class="tech-note-body" style="margin-bottom:0.4rem;">'
                    f'<div class="tech-note-item"><i class="ph-bold ph-chart-pie-slice"></i>'
                    f'<span><strong>Summary:</strong> {crop3}, {season3}: {label}. Range across the {len(has)} districts '
                    f'shown: {lo:,.1f}{unit} to {hi:,.1f}{unit}. {n_grey} district(s) in grey have too few records.</span></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                '<div class="tech-note-body">'
                '<div class="tech-note-item"><i class="ph-bold ph-compass"></i>'
                '<span>Unweighted survey sample, one year. District figures from small samples are noisy. '
                'Boundaries: geoBoundaries (geoboundaries.org), CC BY 4.0, source NISR.</span></div>'
                '</div>',
                unsafe_allow_html=True,
            )

# ---------------------------------------------------------------- 4. price outlook
with tab4:
    if forecast is None:
        st.info("Forecast data not available.")
    else:
        with st.container(border=True):
            g = st.selectbox("Select Food Price Group", list(forecast), key="fc_group")

        f = forecast[g]
        hist = pd.DataFrame(f["history"]); fc = pd.DataFrame(f["forecast"])
        for t in (hist, fc):
            t["date"] = pd.to_datetime(t["month"] + "-01")

        bt = f["backtest"]
        mm = hist["value"].iloc[-1] / hist["value"].iloc[-2] - 1
        six_m_change = fc["value"].iloc[-1] / hist["value"].iloc[-1] - 1

        # Plain-English Outlook Banner
        direction_word = "rise" if six_m_change >= 0 else "fall"
        st.markdown(
            f'<div class="takeaway-banner">'
            f'<div class="takeaway-label"><i class="ph-bold ph-chart-line-up"></i> 6-Month Price Outlook // {g}</div>'
            f'<p class="takeaway-text">'
            f'By <strong>{fc["month"].iloc[-1]}</strong>, the consumer price index for <strong>{g}</strong> is '
            f'projected to <strong>{direction_word} by {six_m_change:+.1%}</strong> compared to the last observed '
            f'month ({f["last_observed"]}). Past forecasts for this group had a typical error of '
            f'<span class="takeaway-highlight">±{bt["avg_mape_1_to_6_pct"][f["model"]]:.1f}%</span>.'
            f'</p></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="data-card-grid">'
            + render_data_card(
                f"Forecast {fc['month'].iloc[-1]}",
                f"{fc['value'].iloc[-1]:.0f}",
                pill_text=f"{six_m_change:+.1%} vs {f['last_observed']}",
                pill_tone="green" if six_m_change >= 0 else "amber",
                helper="Projected Consumer Price Index (Feb 2014 baseline = 100).",
                accent="emerald",
                is_mono=True,
                icon="ph-target",
            )
            + render_data_card(
                "Typical backtest error",
                f"{bt['avg_mape_1_to_6_pct'][f['model']]:.1f}%",
                pill_text=f"{bt['skill_vs_naive_pct']:.0f}% lower than 'no change'",
                pill_tone="slate",
                helper="Average percentage difference between past model predictions and actual prices.",
                accent="slate",
                is_mono=True,
                icon="ph-shield-check",
            )
            + render_data_card(
                "Last month's move",
                f"{mm:+.1%}",
                pill_text=f"Observed: {f['last_observed']}",
                pill_tone="amber" if abs(mm) > 0.05 else "slate",
                helper="Month-over-month price change in the latest official NISR release.",
                accent="amber",
                is_mono=True,
                icon="ph-activity",
            )
            + "</div>",
            unsafe_allow_html=True,
        )

        if abs(mm) > 0.05:
            st.warning(f"The latest month moved {mm:+.1%}. Trend-based models extrapolate part of such jumps, so the "
                       "forecast may overshoot or undershoot; the dotted lines show how the other models differ.")

        fc_col1, fc_col2 = st.columns([1.55, 1.05], gap="medium")

        with fc_col1:
            with st.container(border=True):
                st.markdown(
                    f'<div class="card-section-head">'
                    f'<span class="card-section-title"><i class="ph-bold ph-chart-line-up"></i> Observed History & 6-Month Forecast</span>'
                    f'<span class="card-section-badge"><i class="ph-bold ph-cpu"></i> Model: {f["model"]}</span>'
                    f'</div>'
                    f'<div class="card-plain-explainer">'
                    f'The solid dark line shows historical prices. The green line and shaded band show the expected '
                    f'trajectory and 80% likely range over the next 6 months.'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                fig = go.Figure()
                fig.add_trace(go.Scatter(mode="lines", x=hist["date"], y=hist["value"], name="Observed",
                                         line=dict(color="#0f172a", width=2.2)))
                fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=fc["hi80"], line=dict(width=0),
                                         showlegend=False, hoverinfo="skip"))
                fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=fc["lo80"], fill="tonexty",
                                         fillcolor="rgba(21,128,61,0.20)", line=dict(width=0), name="80% range"))
                last = hist.iloc[[-1]]
                fig.add_trace(go.Scatter(mode="lines+markers", x=pd.concat([last["date"], fc["date"]]),
                                         y=pd.concat([last["value"], fc["value"]]), name=f"Forecast ({f['model']})",
                                         line=dict(color="#15803d", width=3), marker=dict(size=6, color="#15803d")))
                for mname, vals in f["alternatives"].items():
                    if mname != f["model"] and not mname.startswith("naive"):
                        fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=vals, name=mname,
                                                 line=dict(width=1.4, dash="dot")))
                fig.update_layout(height=370, margin=dict(l=4, r=4, t=10, b=8), font=PLOTLY_FONT,
                                  hovermode="x unified", xaxis=dict(**AXIS_STYLE),
                                  yaxis=dict(**AXIS_STYLE, title="Index (Feb 2014 = 100)"),
                                  legend=dict(orientation="h", y=-0.22, font=dict(color="#0f172a", size=11)),
                                  paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
                st.plotly_chart(fig, width="stretch", config=TOUCH_SAFE_CONFIG)

        with fc_col2:
            with st.container(border=True):
                st.markdown(
                    '<div class="card-section-head">'
                    '<span class="card-section-title"><i class="ph-bold ph-calendar"></i> Monthly Forecast Table</span>'
                    '<span class="card-section-badge"><i class="ph-bold ph-clock"></i> Next 6 Months</span>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                st.dataframe(
                    fc[["month", "value", "lo80", "hi80", "yoy_pct"]].rename(columns={
                        "value": "forecast index", "lo80": "low (80%)", "hi80": "high (80%)",
                        "yoy_pct": "vs same month last year %"}),
                    hide_index=True,
                    width="stretch",
                    column_config={
                        "month": st.column_config.TextColumn("Month"),
                        "forecast index": st.column_config.NumberColumn("Forecast", format="%.1f"),
                        "low (80%)": st.column_config.NumberColumn("Low (80%)", format="%.1f"),
                        "high (80%)": st.column_config.NumberColumn("High (80%)", format="%.1f"),
                        "vs same month last year %": st.column_config.NumberColumn("YoY %", format="%+.1f%%"),
                    },
                )

        with st.expander("Backtest Validation & Forecast Limitations"):
            st.markdown(
                f'<div class="tech-note-body">'
                f'<div class="tech-note-item"><i class="ph-bold ph-clock-counter-clockwise"></i>'
                f'<span><strong>Backtest:</strong> {bt["origins"]} forecast starts from {bt["first_origin"]} to {bt["last_origin"]}, '
                f'each forecasting 1 to 6 months ahead. The ranges come from those past errors.</span></div>'
                f'<div class="tech-note-item"><i class="ph-bold ph-info"></i>'
                f'<span>{bt["note"]} National index (all Rwanda); rural food prices have risen faster than the national '
                f'average. This forecasts price indices only, not crop yields or farm-gate prices.</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )   