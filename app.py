"""Rwanda Crop Timing Advisor - Streamlit app.

Four tabs: crop explorer, compare crops, district map, price outlook.
All data is read from pre-computed files in data/ (see scripts/ for how they are built).
"""
import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / "data"
PROC = DATA / "processed"

st.set_page_config(page_title="Rwanda Crop Timing Advisor", layout="wide")
st.title("Rwanda Crop Timing Advisor")
st.caption("When crops are harvested, where they are grown, and how food prices behave. "
           "NISR Agricultural Household Survey 2024 and Consumer Price Index to September 2026.")


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
tab1, tab2, tab3, tab4 = st.tabs(["Crop explorer", "Compare crops", "District map", "Price outlook"])

# ---------------------------------------------------------------- 1. crop explorer
with tab1:
    c_a, c_b = st.columns(2)
    crop = c_a.selectbox("Crop", sorted(cal["crop"].unique()), key="ex_crop")
    seasons = sorted(cal.loc[cal["crop"] == crop, "season"].unique())
    season = c_b.selectbox("Season", seasons, key="ex_season")
    row = cal[(cal["crop"] == crop) & (cal["season"] == season)].iloc[0]

    m1, m2, m3 = st.columns(3)
    m1.metric("Most common harvest window", row["peak_harvest_window"],
              f"{row['peak_window_share']:.0%} of plots with a stated window", delta_arrow="off")
    m2.metric("Most common sowing window",
              row["peak_sowing_window"] if pd.notna(row["peak_sowing_window"]) else "n/a")
    if pd.notna(row["yield_kg_per_ha_median"]):
        m3.metric("Median yield (kg/ha)", f"{int(row['yield_kg_per_ha_median']):,}",
                  f"middle half: {int(row['yield_kg_per_ha_p25']):,} to {int(row['yield_kg_per_ha_p75']):,}",
                  delta_color="off", delta_arrow="off")
    else:
        m3.metric("Median yield (kg/ha)", "n/a")

    if row["share_window_unspecified"] > 0.2:
        st.warning(f"{row['share_window_unspecified']:.0%} of {crop} records have no specific harvest window "
                   "(typical for perennial or year-round crops), so the pattern below covers only the rest.")

    if windows:
        w = pd.DataFrame(windows)
        w = w[(w["crop"] == crop) & (w["season"] == season)].sort_values("order")
        w = w.assign(label=w["order"].astype(str) + ". " + w["window"])  # numbered so labels stay in time order
        st.markdown("**When the harvest happens** (share of plots with a stated window)")
        st.bar_chart(w.set_index("label")["share"])

    group = row["cpi_group"]
    st.markdown("**Typical consumer price pattern**")
    if seasonal and group and group in seasonal:
        st.caption(f"CPI group: {group}. All crops in a group share the same price pattern; "
                   "crops differ only through their harvest timing.")
        s_idx = pd.Series(seasonal[group])
        xl = [k[3:] for k in s_idx.index]
        pf = go.Figure(go.Scatter(x=xl, y=s_idx.values, mode="lines+markers", name="Seasonal price index",
                                  line=dict(color="#2f7d4f", width=3)))
        if pd.notna(row.get("peak_approx_month")):
            hm = int(row["peak_approx_month"]) - 1
            pf.add_trace(go.Scatter(x=[xl[hm]], y=[s_idx.values[hm]], mode="markers", name="Harvest month",
                                    marker=dict(size=13, color="#c2410c")))
        pf.add_hline(y=1.0, line_dash="dot", line_color="#9ca3af")
        pf.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.25),
                         yaxis=dict(title="index (1.0 = average)", range=[min(s_idx.min(), 0.97) - 0.02, max(s_idx.max(), 1.03) + 0.02]),
                         paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(pf)
        if row["cpi_mapping_confidence"] == "probable_verify":
            st.warning(f"{crop} is assumed to follow the '{group}' price group. This mapping is unverified.")
        if pd.notna(row.get("price_gain_hold_3m_pct")):
            p1, p2, p3 = st.columns(3)
            p1.metric("Price index at harvest", f"{row['price_index_at_harvest']:.3f}",
                      "cheaper than average" if row["harvest_in_cheap_season"] else "about average or higher",
                      delta_color="off", delta_arrow="off")
            if row["price_gain_hold_3m_pct"] > 0:
                p2.metric("Best month within 3 months", row["best_month_within_3m"][3:],
                          f"+{row['price_gain_hold_3m_pct']:.1f}% vs harvest month")
            else:
                p2.metric("Best month within 3 months", row["best_month_within_3m"][3:],
                          "harvest month is already the best", delta_color="off", delta_arrow="off")
            p3.metric("Best gain within 6 months", f"+{row['price_gain_hold_6m_pct']:.1f}%")
            st.caption("Consumer price index, not farm-gate price. The gain ignores storage costs and "
                       "post-harvest losses, which the survey does not measure.")
    else:
        st.info("Price pattern not available for this crop (no matching CPI food group).")
    st.caption(f"Based on {int(row['n_entries']):,} survey records, unweighted. "
               "One survey year: descriptive, not a forecast.")

# ---------------------------------------------------------------- 2. compare crops
with tab2:
    st.markdown("**Which crops are harvested when prices are low, and gain most from waiting?**")
    k1, k2 = st.columns(2)
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
        fig = go.Figure(go.Bar(x=d[col], y=d["crop"], orientation="h", marker_color="#2f7d4f", text=d[col].round(2),
                               textposition="outside", cliponaxis=False))
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(height=max(280, 28 * len(d) + 80), margin=dict(l=0, r=10, t=10, b=0),
                          xaxis_title=metric_name, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig)
        show = d[["rank", "crop", "peak_harvest_window", "cpi_group", "price_index_at_harvest", "best_month_within_3m",
                  "price_gain_hold_3m_pct", "price_gain_hold_6m_pct", "yield_kg_per_ha_median",
                  "share_window_unspecified", "cpi_mapping_confidence"]].rename(columns={
            "peak_harvest_window": "peak harvest", "cpi_group": "price group", "price_index_at_harvest": "price index at harvest",
            "best_month_within_3m": "best month (3m)", "price_gain_hold_3m_pct": "gain 3m %", "price_gain_hold_6m_pct": "gain 6m %",
            "yield_kg_per_ha_median": "median yield kg/ha", "share_window_unspecified": "no stated window",
            "cpi_mapping_confidence": "mapping"})
        show["best month (3m)"] = show["best month (3m)"].str[3:]
        show["no stated window"] = (show["no stated window"] * 100).round(0).astype(int).astype(str) + "%"
        st.dataframe(show, hide_index=True)
        st.caption("Crops in the same price group with the same harvest month tie by construction, because the price "
                   "pattern is measured per food group, not per crop. Yields are not comparable across crops. "
                   "Gains are consumer-price index changes and ignore storage costs and losses. "
                   "'assumed' and 'probable_verify' mappings are not confirmed against NISR's CPI methodology.")

# ---------------------------------------------------------------- 3. district map
with tab3:
    if district is None or geo is None:
        st.info("District data not available.")
    else:
        dc = pd.DataFrame(district)
        st.markdown("**Where is each crop grown, and how does yield differ by district?**")
        q1, q2, q3 = st.columns(3)
        season3 = q1.selectbox("Season", sorted(dc["season"].unique()), key="map_season")
        crops3 = sorted(dc.loc[dc["season"] == season3, "crop"].unique())
        crop3 = q2.selectbox("Crop", crops3, index=crops3.index("Irish potato") if "Irish potato" in crops3 else 0,
                             key="map_crop")
        mode = q3.radio("Show", ["Share of crop entries (%)", "Median yield (kg/ha)"], key="map_metric")

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

        hover = (m["district"] + "<br>" + m["value"].map(lambda v: "n/a" if pd.isna(v) else f"{v:,.1f}{unit}") +
                 "<br>records: " + m["n_entries"].fillna(0).astype(int).astype(str))
        # MapLibre-based map with a blank background: no tiles or outside files are fetched
        fig = go.Figure()
        fig.add_trace(go.Choroplethmap(geojson=geo, featureidkey="properties.district", locations=m["district"],
                                       z=[0] * len(m), colorscale=[[0, "#d9dde2"], [1, "#d9dde2"]], showscale=False,
                                       marker_line_color="#ffffff", marker_line_width=0.8, hoverinfo="skip"))
        if not has.empty:
            fig.add_trace(go.Choroplethmap(geojson=geo, featureidkey="properties.district", locations=has["district"],
                                           z=has["value"], colorscale="YlGn", marker_line_color="#ffffff",
                                           marker_line_width=0.8, hovertext=hover[has.index], hoverinfo="text",
                                           colorbar=dict(title=dict(text=unit.strip() or "%"), thickness=12)))
        fig.update_layout(map=dict(style="white-bg", center=dict(lat=-1.95, lon=29.9), zoom=7.4),
                          height=520, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig)

        n_grey = len(m) - len(has)
        if has.empty:
            st.warning("Not enough survey records in any district for this choice.")
        else:
            lo, hi = has["value"].min(), has["value"].max()
            st.caption(f"{crop3}, {season3}: {label}. Range across the {len(has)} districts shown: "
                       f"{lo:,.1f}{unit} to {hi:,.1f}{unit}. {n_grey} district(s) in grey have too few records.")
        if season3 == "Season C":
            st.warning("Season C has very few records per district, so most of the map is grey.")
        st.caption("Unweighted survey sample, one year. District figures from small samples are noisy. "
                   "Boundaries: geoBoundaries (geoboundaries.org), CC BY 4.0, source NISR.")

# ---------------------------------------------------------------- 4. price outlook
with tab4:
    if forecast is None:
        st.info("Forecast data not available.")
    else:
        g = st.selectbox("Price group", list(forecast), key="fc_group")
        f = forecast[g]
        hist = pd.DataFrame(f["history"]); fc = pd.DataFrame(f["forecast"])
        for t in (hist, fc):
            t["date"] = pd.to_datetime(t["month"] + "-01")
        fig = go.Figure()
        fig.add_trace(go.Scatter(mode="lines", x=hist["date"], y=hist["value"], name="Observed", line=dict(color="#1f2937", width=2)))
        fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=fc["hi80"], line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=fc["lo80"], fill="tonexty", fillcolor="rgba(47,125,79,0.18)",
                                 line=dict(width=0), name="80% range"))
        last = hist.iloc[[-1]]
        fig.add_trace(go.Scatter(mode="lines", x=pd.concat([last["date"], fc["date"]]), y=pd.concat([last["value"], fc["value"]]),
                                 name=f"Forecast ({f['model']})", line=dict(color="#2f7d4f", width=3)))
        for mname, vals in f["alternatives"].items():
            if mname != f["model"] and not mname.startswith("naive"):
                fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=vals, name=mname, line=dict(width=1, dash="dot")))
        fig.update_layout(height=420, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Index (Feb 2014 = 100)",
                          legend=dict(orientation="h", y=-0.2), paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig)

        bt = f["backtest"]
        mm = hist["value"].iloc[-1] / hist["value"].iloc[-2] - 1
        o1, o2, o3 = st.columns(3)
        o1.metric(f"Forecast {fc['month'].iloc[-1]}", f"{fc['value'].iloc[-1]:.0f}",
                  f"{fc['value'].iloc[-1] / hist['value'].iloc[-1] - 1:+.1%} vs {f['last_observed']}", delta_color="off", delta_arrow="off")
        o2.metric("Typical backtest error", f"{bt['avg_mape_1_to_6_pct'][f['model']]:.1f}%",
                  f"{bt['skill_vs_naive_pct']:.0f}% lower than 'no change'", delta_color="off", delta_arrow="off")
        o3.metric("Last month's move", f"{mm:+.1%}", f["last_observed"], delta_color="off", delta_arrow="off")
        if abs(mm) > 0.05:
            st.warning(f"The latest month moved {mm:+.1%}. Trend-based models extrapolate part of such jumps, so the "
                       "forecast may overshoot or undershoot; the dotted lines show how the other models differ.")
        st.dataframe(fc[["month", "value", "lo80", "hi80", "yoy_pct"]].rename(columns={
            "value": "forecast index", "lo80": "low (80%)", "hi80": "high (80%)", "yoy_pct": "vs same month last year %"}),
            hide_index=True)
        st.caption(f"Backtest: {bt['origins']} forecast starts from {bt['first_origin']} to {bt['last_origin']}, "
                   "each forecasting 1 to 6 months ahead. The ranges come from those past errors. "
                   f"{bt['note']} National index (all Rwanda); rural food prices have risen faster than the national "
                   "average. This forecasts price indices only, not crop yields or farm-gate prices.")
