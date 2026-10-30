"""Detail views for officers and analysts, written to be readable by non-specialists."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.state_manager import get_active_index, sync_crop, sync_season
from components.text import group_phrase, month_full, season_label, vs_average_text

FONT = dict(family="Inter, sans-serif", color="#F8FAFC", size=12)
AXIS = dict(tickfont=dict(family="JetBrains Mono, monospace", color="#94A3B8", size=11),
            title_font=dict(family="Plus Jakarta Sans, sans-serif", color="#F8FAFC", size=12),
            gridcolor="rgba(255,255,255,0.06)", linecolor="rgba(255,255,255,0.1)", linewidth=1,
            zerolinecolor="rgba(255,255,255,0.2)", fixedrange=True)
CFG = {"displayModeBar": False, "responsive": True}
EMERALD, GOLD, MUTED = "#10B981", "#FBBF24", "#334155"
CLEAR = "rgba(0,0,0,0)"


def title(icon, text, sub):
    st.markdown(f"## <span style='color:#10B981;'>:material/{icon}:</span> {text}", unsafe_allow_html=True)
    st.caption(sub)


def render_crop_explorer(cal, windows, seasonal):
    title("search", "Crop details", "The full harvest and price picture for one crop in one season.")
    a, b = st.columns(2)
    crops = sorted(cal["crop"].unique())
    crop = a.selectbox("Crop", crops, index=get_active_index(crops, "master_crop"), key="exp_crop",
                       on_change=sync_crop, args=("exp_crop",))
    seasons = sorted(cal.loc[cal["crop"] == crop, "season"].unique())
    season = b.selectbox("Season", seasons, index=get_active_index(seasons, "master_season"), key="exp_season",
                         on_change=sync_season, args=("exp_season",), format_func=season_label)
    row = cal[(cal["crop"] == crop) & (cal["season"] == season)].iloc[0]

    has_y = pd.notna(row["yield_kg_per_ha_median"])
    m1, m2, m3 = st.columns(3)
    m1.metric("Most common harvest time", str(row["peak_harvest_window"]), f"{row['peak_window_share']:.0%} of farmers")
    m2.metric("Most common planting time", str(row["peak_sowing_window"]) if pd.notna(row["peak_sowing_window"]) else "not clear")
    m3.metric("Typical harvest per hectare (kg)", f"{int(row['yield_kg_per_ha_median']):,}" if has_y else "n/a",
              f"most plots: {int(row['yield_kg_per_ha_p25']):,} to {int(row['yield_kg_per_ha_p75']):,}" if has_y else "")
    if row["share_window_unspecified"] > 0.2:
        st.warning(f"{row['share_window_unspecified']:.0%} of {crop} records gave no specific harvest time "
                   "(common for crops harvested all year), so the chart covers only the rest.")

    left, right = st.columns([1, 1.1], gap="medium")
    with left:
        if windows:
            w = pd.DataFrame(windows)
            w = w[(w["crop"] == crop) & (w["season"] == season)].sort_values("order")
            w = w.assign(label=w["order"].astype(str) + ". " + w["window"])
            with st.container(border=True):
                st.markdown("#### When farmers harvest")
                pk = w["share"].max() if not w.empty else 0
                f = go.Figure(go.Bar(x=w["label"], y=w["share"], marker=dict(color=[EMERALD if v == pk else MUTED for v in w["share"]], cornerradius=4),
                                     text=(w["share"] * 100).round(0).astype(int).astype(str) + "%", textposition="outside",
                                     textfont=dict(color="#F8FAFC", size=10), cliponaxis=False))
                f.update_layout(height=300, margin=dict(l=4, r=4, t=10, b=8), font=FONT, paper_bgcolor=CLEAR, plot_bgcolor=CLEAR,
                                xaxis=dict(**AXIS, tickangle=-30), yaxis=dict(**AXIS, tickformat=".0%", range=[0, max(pk * 1.25, 0.1)]))
                st.plotly_chart(f, width="stretch", config=CFG)
                st.caption("Share of farmers who gave each harvest time. The tallest bar is highlighted.")
    group = row["cpi_group"]
    with right:
        with st.container(border=True):
            st.markdown("#### How prices change through the year")
            if seasonal and group and group in seasonal:
                s = pd.Series(seasonal[group])
                xl = [k[3:] for k in s.index]
                f = go.Figure(go.Scatter(x=xl, y=s.values, mode="lines+markers", name="Price level", line=dict(color=EMERALD, width=3),
                                         marker=dict(size=6, color=EMERALD), fill="tozeroy", fillcolor="rgba(16,185,129,0.1)"))
                if pd.notna(row.get("peak_approx_month")):
                    hm = int(row["peak_approx_month"]) - 1
                    f.add_trace(go.Scatter(x=[xl[hm]], y=[s.values[hm]], mode="markers", name="Harvest month",
                                           marker=dict(size=14, color=GOLD, line=dict(color="#0B1120", width=2))))
                f.add_hline(y=1.0, line_dash="dot", line_color="rgba(255,255,255,0.3)")
                f.update_layout(height=300, margin=dict(l=4, r=4, t=10, b=8), font=FONT, hovermode="x unified", paper_bgcolor=CLEAR, plot_bgcolor=CLEAR,
                                legend=dict(orientation="h", y=-0.22, font=dict(color="#94A3B8", size=11)), xaxis=dict(**AXIS),
                                yaxis=dict(**AXIS, title="1.0 = yearly average", range=[min(s.min(), 0.97) - 0.02, max(s.max(), 1.03) + 0.02]))
                st.plotly_chart(f, width="stretch", config=CFG)
                st.caption(f"Pattern for {group_phrase(group)} across Rwanda. Above the dotted line means dearer than average. "
                           "Crops in the same group share one pattern and differ only by harvest month.")
            else:
                st.info("No price pattern for this crop: the national price statistics have no matching group.")
    if row["cpi_mapping_confidence"] == "probable_verify" and group:
        st.warning(f"We assume {crop} prices follow {group_phrase(group)}. This is our best estimate and has not been confirmed.")

    if seasonal and group and group in seasonal and pd.notna(row.get("price_gain_hold_3m_pct")):
        p1, p2, p3 = st.columns(3)
        p1.metric("Price in the harvest month", vs_average_text(row["price_index_at_harvest"]).replace("the yearly average", "average"),
                  "cheaper than usual" if row["harvest_in_cheap_season"] else "not a cheap month")
        p2.metric("Best month to sell (within 3 months)", month_full(row["best_month_within_3m"]),
                  f"+{row['price_gain_hold_3m_pct']:.1f}% vs harvest month" if row["price_gain_hold_3m_pct"] > 0 else "harvest month is best")
        p3.metric("Best gain from waiting up to 6 months", f"+{row['price_gain_hold_6m_pct']:.1f}%")
        st.caption("These are changes in consumer prices across Rwanda, not what a buyer pays at the farm gate. "
                   "They ignore storage costs and crop losses, which the survey does not measure.")
    st.caption(f"Based on {int(row['n_entries']):,} survey records from one year (2024), not adjusted to represent the whole country.")


def render_compare_crops(cal):
    title("balance", "Compare crops", "Which crops are harvested when prices are low and gain most from waiting?")
    k1, k2 = st.columns([3, 2])
    seasons = sorted(cal["season"].unique())
    season = k1.selectbox("Season", seasons, index=get_active_index(seasons, "master_season"), key="cmp_season",
                          on_change=sync_season, args=("cmp_season",), format_func=season_label)
    METRICS = {"Gain from waiting up to 3 months (%)": ("price_gain_hold_3m_pct", False),
               "Best gain from waiting up to 6 months (%)": ("price_gain_hold_6m_pct", False),
               "Harvest-month price compared with average (%), lowest first": ("price_vs_avg_pct", True)}
    name = k2.selectbox("Rank crops by", list(METRICS))
    col, asc = METRICS[name]
    only_ok = st.checkbox("Only crops whose price group is not an assumption", value=False)

    d = cal[cal["season"] == season].copy()
    d["price_vs_avg_pct"] = (d["price_index_at_harvest"] - 1) * 100
    d = d[d[col].notna()]
    if only_ok:
        d = d[d["cpi_mapping_confidence"] == "assumed"]
    if d.empty:
        st.info("No crops with a price pattern match these choices.")
        return
    d = d.sort_values(col, ascending=asc)
    d["rank"] = d[col].rank(method="min", ascending=asc).astype(int)
    with st.container(border=True):
        st.markdown(f"#### Ranking, {season_label(season)}")
        f = go.Figure(go.Bar(x=d[col], y=d["crop"], orientation="h", marker=dict(color=[EMERALD if r <= 3 else MUTED for r in d["rank"]], cornerradius=4),
                             text=d[col].round(1), textposition="outside", textfont=dict(color="#F8FAFC", size=11), cliponaxis=False))
        f.update_yaxes(autorange="reversed", **AXIS)
        f.update_xaxes(**AXIS, title=name)
        f.update_layout(height=max(280, 28 * len(d) + 70), margin=dict(l=4, r=45, t=10, b=10), font=FONT, paper_bgcolor=CLEAR, plot_bgcolor=CLEAR)
        st.plotly_chart(f, width="stretch", config=CFG)
    show = d[["rank", "crop", "peak_harvest_window", "cpi_group", "price_vs_avg_pct", "best_month_within_3m", "price_gain_hold_3m_pct",
              "price_gain_hold_6m_pct", "cpi_mapping_confidence"]].rename(columns={
        "rank": "Rank", "crop": "Crop", "peak_harvest_window": "Harvest time", "cpi_group": "Price group",
        "price_vs_avg_pct": "Harvest price vs average %", "best_month_within_3m": "Best month to sell",
        "price_gain_hold_3m_pct": "Gain 3 months %", "price_gain_hold_6m_pct": "Gain 6 months %", "cpi_mapping_confidence": "Price group certainty"})
    show["Best month to sell"] = show["Best month to sell"].map(month_full)
    show["Harvest price vs average %"] = show["Harvest price vs average %"].round(1)
    show["Price group certainty"] = show["Price group certainty"].map({"assumed": "reasonable match", "probable_verify": "unconfirmed guess"})
    st.dataframe(show, hide_index=True, width="stretch")
    st.caption("Crops in the same price group with the same harvest month tie, because prices are measured per food group, "
               "not per crop. Gains are changes in a consumer price index and ignore storage costs and losses. "
               "'Unconfirmed guess' means we assume the crop follows that group.")


def render_district_map(cal, district_data, geo):
    title("map", "Where it grows", "How common a crop is in each district, or how much it yields there.")
    if not district_data or not geo:
        st.info("District data not available.")
        return
    dc = pd.DataFrame(district_data)
    q1, q2, q3 = st.columns([1, 1.2, 1.4])
    seasons = sorted(dc["season"].unique())
    season = q1.selectbox("Season", seasons, index=get_active_index(seasons, "master_season"), key="map_season",
                          on_change=sync_season, args=("map_season",), format_func=season_label)
    crops = sorted(dc.loc[dc["season"] == season, "crop"].unique())
    crop = q2.selectbox("Crop", crops, index=get_active_index(crops, "master_crop"), key="map_crop",
                        on_change=sync_crop, args=("map_crop",))
    mode = q3.radio("Show", ["How common it is (%)", "Typical harvest per hectare (kg)"], horizontal=True, key="map_metric")

    all_d = pd.DataFrame({"district": [f["properties"]["district"] for f in geo["features"]]})
    m = all_d.merge(dc[(dc["season"] == season) & (dc["crop"] == crop)], on="district", how="left")
    totals = dc[dc["season"] == season].drop_duplicates("district").set_index("district")["district_total_entries"]
    m["district_total_entries"] = m["district"].map(totals)
    if mode.startswith("How"):
        m["value"] = m["share_of_entries"] * 100
        m.loc[m["district_total_entries"].fillna(0) < 100, "value"] = None
        m.loc[m["share_of_entries"].isna() & (m["district_total_entries"].fillna(0) >= 100), "value"] = 0.0
        unit = "%"
    else:
        m["value"] = m["yield_kg_per_ha_median"]
        unit = " kg/ha"
    has = m.dropna(subset=["value"])
    if has.empty:
        st.warning("Not enough survey records in any district for this choice.")
    else:
        top = has.sort_values("value", ascending=False).iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Highest district", str(top["district"]), f"{top['value']:,.1f}{unit}")
        c2.metric("Range across districts", f"{has['value'].min():,.1f} to {has['value'].max():,.1f}{unit}")
        c3.metric("Districts with enough data", f"{len(has)} of {len(m)}", f"{len(m) - len(has)} shown in grey")
    hover = m["district"] + "<br>" + m["value"].map(lambda v: "not enough data" if pd.isna(v) else f"{v:,.1f}{unit}")
    with st.container(border=True):
        st.markdown(f"#### {crop}, {season_label(season)}")
        f = go.Figure()
        f.add_trace(go.Choroplethmap(geojson=geo, featureidkey="properties.district", locations=m["district"], z=[0] * len(m),
                                     colorscale=[[0, "#1e293b"], [1, "#1e293b"]], showscale=False,
                                     marker_line_color="rgba(255,255,255,0.1)", marker_line_width=1.0, hoverinfo="skip"))
        if not has.empty:
            f.add_trace(go.Choroplethmap(geojson=geo, featureidkey="properties.district", locations=has["district"], z=has["value"],
                                         colorscale="YlGn", marker_line_color="#0B1120", marker_line_width=1.0, hovertext=hover[has.index],
                                         hoverinfo="text", colorbar=dict(title=dict(text=unit.strip(), font=dict(color="#F8FAFC")), tickfont=dict(color="#94A3B8"))))
        f.update_layout(map=dict(style="carto-darkmatter", center=dict(lat=-1.95, lon=29.9), zoom=7.3), height=460,
                        margin=dict(l=0, r=0, t=5, b=0), font=FONT, paper_bgcolor=CLEAR)
        st.plotly_chart(f, width="stretch", config=CFG)
    if season == "Season C":
        st.warning("Season C has very few survey records per district, so most of the map is grey.")
    st.caption("'How common' is the crop's share of everything surveyed farmers grow in that district, not total harvest. "
               "Grey districts have too few survey records. Figures come from one survey year and are not adjusted for "
               "population, so small districts can look uneven. Boundaries: geoBoundaries (CC BY 4.0), source NISR.")


def render_price_outlook(forecast):
    title("trending_up", "Price forecast", "Where food prices are likely heading over the next six months.")
    if not forecast:
        st.info("Forecast data not available.")
        return
    names = {"Food (all)": "All food", "Bread and cereals": "Cereals and bread", "Vegetables": "Vegetables"}
    g = st.selectbox("Which prices?", list(forecast), key="fc_group", format_func=lambda x: names.get(x, x))
    f = forecast[g]
    hist, fc = pd.DataFrame(f["history"]), pd.DataFrame(f["forecast"])
    for t in (hist, fc):
        t["date"] = pd.to_datetime(t["month"] + "-01")
    bt = f["backtest"]
    mm = hist["value"].iloc[-1] / hist["value"].iloc[-2] - 1
    six = fc["value"].iloc[-1] / hist["value"].iloc[-1] - 1
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Expected price level in {fc['month'].iloc[-1]}", f"{fc['value'].iloc[-1]:.0f}", f"{six:+.1%} from {f['last_observed']}")
    m2.metric("How far off past forecasts were", f"about {bt['avg_mape_1_to_6_pct'][f['model']]:.1f}%", f"{bt['skill_vs_naive_pct']:.0f}% better than 'no change'")
    m3.metric("Change in the latest month", f"{mm:+.1%}", f["last_observed"])
    if abs(mm) > 0.05:
        st.warning(f"Prices moved {mm:+.1%} in the latest month. Forecast models tend to carry part of a sudden jump forward, "
                   "so treat the line as a range. The dotted lines show how other models differ.")
    with st.container(border=True):
        st.markdown(f"#### Six-month forecast ({f['model']})")
        fig = go.Figure()
        fig.add_trace(go.Scatter(mode="lines", x=hist["date"], y=hist["value"], name="Actual", line=dict(color="#94A3B8", width=2.2)))
        fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=fc["hi80"], line=dict(width=0), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=fc["lo80"], fill="tonexty", fillcolor="rgba(16,185,129,0.15)", line=dict(width=0), name="Likely range (80%)"))
        last = hist.iloc[[-1]]
        fig.add_trace(go.Scatter(mode="lines+markers", x=pd.concat([last["date"], fc["date"]]), y=pd.concat([last["value"], fc["value"]]),
                                 name="Forecast", line=dict(color=EMERALD, width=3), marker=dict(size=6, color=EMERALD)))
        for mname, vals in f["alternatives"].items():
            if mname != f["model"] and not mname.startswith("naive"):
                fig.add_trace(go.Scatter(mode="lines", x=fc["date"], y=vals, name=mname, line=dict(color="rgba(255,255,255,0.3)", width=1.4, dash="dot")))
        fig.update_layout(height=370, margin=dict(l=4, r=4, t=10, b=8), font=FONT, hovermode="x unified", paper_bgcolor=CLEAR, plot_bgcolor=CLEAR,
                          xaxis=dict(**AXIS), yaxis=dict(**AXIS, title="Price level (Feb 2014 = 100)"),
                          legend=dict(orientation="h", y=-0.22, font=dict(color="#94A3B8", size=11)))
        st.plotly_chart(fig, width="stretch", config=CFG)
    st.dataframe(fc[["month", "value", "lo80", "hi80", "yoy_pct"]].rename(columns={
        "month": "Month", "value": "Forecast", "lo80": "Low end", "hi80": "High end", "yoy_pct": "Change vs same month last year %"}),
        hide_index=True, width="stretch")
    st.caption(f"How we checked: the model was tested on {bt['origins']} past forecasts made between {bt['first_origin']} and "
               f"{bt['last_origin']}, each looking 1 to 6 months ahead. The likely range comes from those past errors. {bt['note']} "
               "This uses the national price index; rural food prices have risen faster. It forecasts consumer prices only, "
               "not crop harvests or the price a farmer is paid.")
