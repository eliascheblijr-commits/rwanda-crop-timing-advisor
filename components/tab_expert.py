"""Expert Analytical Views. Premium Dark Native redesign."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from components.state_manager import sync_crop, sync_season, get_active_index

PLOTLY_FONT = dict(family="Inter, sans-serif", color="#F8FAFC", size=12)
AXIS_STYLE = dict(
    tickfont=dict(family="JetBrains Mono, monospace", color="#94A3B8", size=11),
    title_font=dict(family="Plus Jakarta Sans, sans-serif", color="#F8FAFC", size=12),
    gridcolor="rgba(255,255,255,0.06)",
    linecolor="rgba(255,255,255,0.1)",
    linewidth=1,
    zerolinecolor="rgba(255,255,255,0.2)",
    fixedrange=True,
)
TOUCH_SAFE_CONFIG = {"displayModeBar": False, "responsive": True}
ACCENT_EMERALD = "#10B981"
ACCENT_GOLD = "#FBBF24"

def render_crop_explorer(cal: pd.DataFrame, windows: list, seasonal: dict):
    st.markdown("## <span style='color: #10B981;'>:material/search:</span> Crop Explorer", unsafe_allow_html=True)
    st.markdown("---")

    c_a, c_b = st.columns(2)
    all_crops = sorted(cal["crop"].unique())
    crop_idx = get_active_index(all_crops, "master_crop")
    crop = c_a.selectbox("Select Crop", all_crops, index=crop_idx, key="exp_crop", on_change=sync_crop, args=("exp_crop",))
    
    seasons = sorted(cal.loc[cal["crop"] == crop, "season"].unique())
    season_idx = get_active_index(seasons, "master_season")
    season = c_b.selectbox("Select Season", seasons, index=season_idx, key="exp_season", on_change=sync_season, args=("exp_season",))

    row = cal[(cal["crop"] == crop) & (cal["season"] == season)].iloc[0]
    st.markdown("<br>", unsafe_allow_html=True)

    sowing_val = row["peak_sowing_window"] if pd.notna(row["peak_sowing_window"]) else "n/a"
    yield_val = f"{int(row['yield_kg_per_ha_median']):,}" if pd.notna(row["yield_kg_per_ha_median"]) else "n/a"
    yield_pill = f"P25-P75: {int(row['yield_kg_per_ha_p25']):,} to {int(row['yield_kg_per_ha_p75']):,}" if yield_val != "n/a" else ""

    m1, m2, m3 = st.columns(3)
    m1.metric("Peak Harvest Window", str(row["peak_harvest_window"]), f"{row['peak_window_share']:.0%} share")
    m2.metric("Peak Sowing Window", str(sowing_val), "Primary Window")
    m3.metric("Median Yield (kg/ha)", str(yield_val), yield_pill)

    if row["share_window_unspecified"] > 0.2:
        st.warning(f"{row['share_window_unspecified']:.0%} of {crop} records have no specific harvest window.")

    col_harvest, col_price = st.columns([1, 1.1], gap="medium")

    with col_harvest:
        if windows:
            w = pd.DataFrame(windows)
            w = w[(w["crop"] == crop) & (w["season"] == season)].sort_values("order")
            w = w.assign(label=w["order"].astype(str) + ". " + w["window"])
            with st.container(border=True):
                st.markdown("#### Harvest Distribution")
                peak_s = w["share"].max() if not w.empty else 0
                b_colors = [ACCENT_EMERALD if val == peak_s and peak_s > 0 else "#334155" for val in w["share"]]
                wf = go.Figure(go.Bar(x=w["label"], y=w["share"], marker=dict(color=b_colors, cornerradius=4), text=(w["share"] * 100).round(0).astype(int).astype(str) + "%", textposition="outside", textfont=dict(family="JetBrains Mono, monospace", color="#F8FAFC", size=10), cliponaxis=False))
                wf.update_layout(height=300, margin=dict(l=4, r=4, t=10, b=8), font=PLOTLY_FONT, xaxis=dict(**AXIS_STYLE, title=None, tickangle=-30), yaxis=dict(**AXIS_STYLE, title=None, tickformat=".0%", range=[0, max(peak_s * 1.25, 0.1)]), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(wf, width="stretch", config=TOUCH_SAFE_CONFIG)

    with col_price:
        group = row["cpi_group"]
        with st.container(border=True):
            st.markdown(f"#### Seasonal Price Index ({group if group else 'N/A'})")
            if seasonal and group and group in seasonal:
                s_idx = pd.Series(seasonal[group])
                xl = [k[3:] for k in s_idx.index]
                pf = go.Figure(go.Scatter(x=xl, y=s_idx.values, mode="lines+markers", name="Index", line=dict(color=ACCENT_EMERALD, width=3), marker=dict(size=6, color=ACCENT_EMERALD), fill="tozeroy", fillcolor="rgba(16, 185, 129, 0.1)"))
                if pd.notna(row.get("peak_approx_month")):
                    hm = int(row["peak_approx_month"]) - 1
                    pf.add_trace(go.Scatter(x=[xl[hm]], y=[s_idx.values[hm]], mode="markers", name="Harvest month", marker=dict(size=14, color=ACCENT_GOLD, line=dict(color="#0B1120", width=2))))
                pf.add_hline(y=1.0, line_dash="dot", line_color="rgba(255,255,255,0.3)")
                pf.update_layout(height=300, margin=dict(l=4, r=4, t=10, b=8), font=PLOTLY_FONT, hovermode="x unified", legend=dict(orientation="h", y=-0.22, font=dict(color="#94A3B8", size=11)), xaxis=dict(**AXIS_STYLE), yaxis=dict(**AXIS_STYLE, title="Index (1.0 = avg)", range=[min(s_idx.min(), 0.97) - 0.02, max(s_idx.max(), 1.03) + 0.02]), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(pf, width="stretch", config=TOUCH_SAFE_CONFIG)
            else:
                st.info("Price pattern not available for this crop.")

    if seasonal and group and group in seasonal and pd.notna(row.get("price_gain_hold_3m_pct")):
        p1, p2, p3 = st.columns(3)
        p1.metric("CPI at Harvest", f"{row['price_index_at_harvest']:.3f}", "Cheaper than average" if row["harvest_in_cheap_season"] else "Average or higher")
        m3_pill = f"+{row['price_gain_hold_3m_pct']:.1f}% vs harvest" if row["price_gain_hold_3m_pct"] > 0 else "Harvest is best"
        p2.metric("Best Month (3m Hold)", str(row["best_month_within_3m"][3:]), m3_pill)
        p3.metric("Max Gain (6m Hold)", f"+{row['price_gain_hold_6m_pct']:.1f}%", "Max seasonal gain")

def render_compare_crops(cal: pd.DataFrame):
    st.markdown("## <span style='color: #10B981;'>:material/balance:</span> Compare Crops", unsafe_allow_html=True)
    st.markdown("---")

    k1, k2 = st.columns([1, 2])
    seasons = sorted(cal["season"].unique())
    season_idx = get_active_index(seasons, "master_season")
    season2 = k1.selectbox("Season", seasons, index=season_idx, key="cmp_season", on_change=sync_season, args=("cmp_season",))
    
    METRICS = {
        "Price gain from holding up to 3 months (%)": ("price_gain_hold_3m_pct", False),
        "Best price gain within 6 months (%)": ("price_gain_hold_6m_pct", False),
        "Price index at harvest (lowest = harvested when prices are cheapest)": ("price_index_at_harvest", True),
    }
    metric_name = k2.selectbox("Rank by", list(METRICS))
    col, ascending = METRICS[metric_name]

    d = cal[(cal["season"] == season2) & cal[col].notna()].copy()
    if d.empty:
        st.info("No crops match these filters.")
        return

    d = d.sort_values(col, ascending=ascending)
    d["rank"] = d[col].rank(method="min", ascending=ascending).astype(int)

    with st.container(border=True):
        st.markdown(f"#### Visual Ranking ({season2})")
        bar_colors = [ACCENT_EMERALD if r <= 3 else "#334155" for r in d["rank"]]
        fig = go.Figure(go.Bar(x=d[col], y=d["crop"], orientation="h", marker=dict(color=bar_colors, cornerradius=4), text=d[col].round(2), textposition="outside", textfont=dict(family="JetBrains Mono, monospace", color="#F8FAFC", size=11), cliponaxis=False))
        fig.update_yaxes(autorange="reversed", **AXIS_STYLE)
        fig.update_xaxes(**AXIS_STYLE, title=metric_name)
        fig.update_layout(height=max(280, 28 * len(d) + 70), margin=dict(l=4, r=45, t=10, b=10), font=PLOTLY_FONT, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch", config=TOUCH_SAFE_CONFIG)

    show = d[["rank", "crop", "cpi_group", "price_index_at_harvest", "price_gain_hold_3m_pct", "price_gain_hold_6m_pct", "yield_kg_per_ha_median"]].rename(columns={"rank": "Rank", "crop": "Crop", "cpi_group": "CPI Group", "price_index_at_harvest": "Harvest CPI", "price_gain_hold_3m_pct": "3m Gain %", "price_gain_hold_6m_pct": "6m Gain %", "yield_kg_per_ha_median": "Median Yield"})
    st.dataframe(show, hide_index=True, width="stretch")

def render_district_map(cal: pd.DataFrame, district_data: list, geo: dict):
    st.markdown("## <span style='color: #10B981;'>:material/map:</span> District Map", unsafe_allow_html=True)
    st.markdown("---")

    if not district_data or not geo:
        st.info("District data not available.")
        return

    dc = pd.DataFrame(district_data)
    q1, q2, q3 = st.columns([1, 1.2, 1.4])
    
    seasons = sorted(dc["season"].unique())
    season_idx = get_active_index(seasons, "master_season")
    season3 = q1.selectbox("Season", seasons, index=season_idx, key="map_season", on_change=sync_season, args=("map_season",))
    
    crops3 = sorted(dc.loc[dc["season"] == season3, "crop"].unique())
    crop_idx = get_active_index(crops3, "master_crop")
    crop3 = q2.selectbox("Crop", crops3, index=crop_idx, key="map_crop", on_change=sync_crop, args=("map_crop",))
    mode = q3.radio("Metric", ["Share of crop entries (%)", "Median yield (kg/ha)"], horizontal=True, key="map_metric")

    all_d = pd.DataFrame({"district": [f["properties"]["district"] for f in geo["features"]]})
    sub = dc[(dc["season"] == season3) & (dc["crop"] == crop3)]
    m = all_d.merge(sub, on="district", how="left")
    totals = dc[dc["season"] == season3].drop_duplicates("district").set_index("district")["district_total_entries"]
    m["district_total_entries"] = m["district"].map(totals)
    
    if mode.startswith("Share"):
        m["value"] = m["share_of_entries"] * 100
        m.loc[m["district_total_entries"].fillna(0) < 100, "value"] = None
        unit = "%"
    else:
        m["value"] = m["yield_kg_per_ha_median"]
        unit = " kg/ha"
        
    if mode.startswith("Share"):
        m.loc[m["share_of_entries"].isna() & (m["district_total_entries"].fillna(0) >= 100), "value"] = 0.0
        
    has = m.dropna(subset=["value"])
    n_grey = len(m) - len(has)

    if not has.empty:
        lo, hi = has["value"].min(), has["value"].max()
        top_dist = has.sort_values("value", ascending=False).iloc[0]
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Highest District", str(top_dist["district"]), f"{top_dist['value']:,.1f}{unit}")
        m2.metric("Observed Range", f"{lo:,.1f} – {hi:,.1f}{unit}", mode.split()[0])
        m3.metric("Coverage", f"{len(has)} of {len(m)}", f"{n_grey} omitted (low data)")
    else:
        st.warning("Not enough survey records in any district for this choice.")

    hover = (m["district"] + "<br>" + m["value"].map(lambda v: "n/a" if pd.isna(v) else f"{v:,.1f}{unit}"))
    with st.container(border=True):
        st.markdown(f"#### {crop3} ({season3}) Choropleth")
        fig = go.Figure()
        fig.add_trace(go.Choroplethmap(geojson=geo, featureidkey="properties.district", locations=m["district"], z=[0]*len(m), colorscale=[[0, "#1e293b"], [1, "#1e293b"]], showscale=False, marker_line_color="rgba(255,255,255,0.1)", marker_line_width=1.0, hoverinfo="skip"))
        if not has.empty:
            fig.add_trace(go.Choroplethmap(geojson=geo, featureidkey="properties.district", locations=has["district"], z=has["value"], colorscale="YlGn", marker_line_color="#0B1120", marker_line_width=1.0, hovertext=hover[has.index], hoverinfo="text", colorbar=dict(title=dict(text=unit.strip() or "%", font=dict(color="#F8FAFC")), tickfont=dict(color="#94A3B8"))))
        fig.update_layout(map=dict(style="carto-darkmatter", center=dict(lat=-1.95, lon=29.9), zoom=7.3), height=460, margin=dict(l=0, r=0, t=5, b=0), font=PLOTLY_FONT, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch", config=TOUCH_SAFE_CONFIG)

def render_price_outlook(forecast: dict):
    st.markdown("## <span style='color: #10B981;'>:material/trending_up:</span> Price Outlook", unsafe_allow_html=True)
    st.markdown("---")

    if not forecast:
        st.info("Forecast data not available.")
        return

    g = st.selectbox("Select Food Price Group", list(forecast), key="fc_group")
    f = forecast[g]
    hist = pd.DataFrame(f["history"])
    fc = pd.DataFrame(f["forecast"])
    for t in (hist, fc):
        t["date"] = pd.to_datetime(t["month"] + "-01")

    bt = f["backtest"]
    mm = hist["value"].iloc[-1] / hist["value"].iloc[-2] - 1
    six_m_change = fc["value"].iloc[-1] / hist["value"].iloc[-1] - 1

    m1, m2, m3 = st.columns(3)
    m1.metric(f"Forecast {fc['month'].iloc[-1]}", f"{fc['value'].iloc[-1]:.0f}", f"{six_m_change:+.1%} vs {f['last_observed']}")
    m2.metric("Backtest Error", f"{bt['avg_mape_1_to_6_pct'][f['model']]:.1f}%", f"{bt['skill_vs_naive_pct']:.0f}% vs naive")
    m3.metric("Last Observed Move", f"{mm:+.1%}", f"{f['last_observed']}")

    fc_col1, fc_col2 = st.columns([1.55, 1.05], gap="medium")
    with fc_col1:
        with st.container(border=True):
            st.markdown(f"#### 6-Month Forecast ({f['model']})")
            fig = go.Figure()
            fig.add_trace(go.Scatter(mode="lines", x=hist["date"], y=hist["value"], name="Observed", line=dict(color="#94A3B8", width=2.2)))
            fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=fc["hi80"], line=dict(width=0), showlegend=False, hoverinfo="skip"))
            fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=fc["lo80"], fill="tonexty", fillcolor="rgba(16,185,129,0.15)", line=dict(width=0), name="80% range"))
            last = hist.iloc[[-1]]
            fig.add_trace(go.Scatter(mode="lines+markers", x=pd.concat([last["date"], fc["date"]]), y=pd.concat([last["value"], fc["value"]]), name=f"Forecast", line=dict(color=ACCENT_EMERALD, width=3), marker=dict(size=6, color=ACCENT_EMERALD)))
            for mname, vals in f["alternatives"].items():
                if mname != f["model"] and not mname.startswith("naive"):
                    fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=vals, name=mname, line=dict(color="rgba(255,255,255,0.3)", width=1.4, dash="dot")))
            fig.update_layout(height=370, margin=dict(l=4, r=4, t=10, b=8), font=PLOTLY_FONT, hovermode="x unified", xaxis=dict(**AXIS_STYLE), yaxis=dict(**AXIS_STYLE, title="Index"), legend=dict(orientation="h", y=-0.22, font=dict(color="#94A3B8", size=11)), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, width="stretch", config=TOUCH_SAFE_CONFIG)

    with fc_col2:
        st.dataframe(fc[["month", "value", "lo80", "hi80", "yoy_pct"]].rename(columns={"value": "Forecast", "lo80": "Low", "hi80": "High", "yoy_pct": "YoY %"}), hide_index=True, width="stretch")  