"""'My crop': the plain-language starting screen for farmers, in English, Kinyarwanda or French."""
import pandas as pd
import streamlit as st

from components.i18n import t
from components.state_manager import get_active_index, sync_crop, sync_season
from components.text import crop_label, group_phrase, month_full, season_label, window_label


def card(icon, color, title):
    st.markdown(f"#### <span style='color:{color};'>:material/{icon}:</span> {title}", unsafe_allow_html=True)


def render(cal: pd.DataFrame, district_data: list, lang: str = "en"):
    st.markdown(f"## <span style='color:#10B981;'>:material/eco:</span> {t('title', lang)}", unsafe_allow_html=True)
    st.caption(t("intro", lang))

    c1, c2 = st.columns(2)
    crops = sorted(cal["crop"].unique())
    crop = c1.selectbox(t("q_crop", lang), crops, index=get_active_index(crops, "master_crop"), key=f"wizard_crop_{lang}",
                        on_change=sync_crop, args=(f"wizard_crop_{lang}",), format_func=lambda c: crop_label(c, lang))
    seasons = sorted(cal.loc[cal["crop"] == crop, "season"].unique())
    season = c2.selectbox(t("q_season", lang), seasons, index=get_active_index(seasons, "master_season"), key=f"wizard_season_{lang}",
                          on_change=sync_season, args=(f"wizard_season_{lang}",), format_func=lambda s: season_label(s, lang))
    row = cal[(cal["crop"] == crop) & (cal["season"] == season)].iloc[0]
    name = crop_label(crop, lang)
    if lang != "en":
        name = name[:1].lower() + name[1:]  # mid-sentence
    if season == "Season C":
        st.info(t("c_info", lang))

    with st.container(border=True):
        card("grass", "#0EA5E9", t("plant_title", lang))
        if pd.notna(row["peak_sowing_window"]):
            st.markdown(t("plant_yes", lang, crop=name, w=window_label(row["peak_sowing_window"], lang)))
        else:
            st.markdown(t("plant_no", lang))

    with st.container(border=True):
        card("shopping_basket", "#10B981", t("harvest_title", lang))
        if pd.notna(row["peak_harvest_window"]):
            st.markdown(t("harvest_yes", lang, w=window_label(row["peak_harvest_window"], lang)))
            st.caption(t("harvest_share", lang, p=f"{row['peak_window_share']:.0%}"))
        else:
            st.markdown(t("harvest_no", lang))

    with st.container(border=True):
        card("payments", "#FBBF24", t("sell_title", lang))
        phrase = group_phrase(row["cpi_group"], lang) if row["cpi_group"] else ""
        g = phrase[:1].upper() + phrase[1:]
        if pd.notna(row.get("price_gain_hold_3m_pct")):
            if row["price_gain_hold_3m_pct"] > 0:
                month = month_full(row["best_month_within_3m"], lang)
                st.markdown(t("sell_wait", lang, crop=name, m=month))
                st.caption(t("sell_wait_cap", lang, g=g, x=f"{row['price_gain_hold_3m_pct']:.0f}", m=month))
            else:
                st.markdown(t("sell_now", lang))
                st.caption(t("sell_now_cap", lang, g=g))
            st.caption(t("sell_disc", lang))
            if row["cpi_mapping_confidence"] == "probable_verify":
                st.caption(t("sell_guess", lang, crop=name))
        else:
            st.markdown(t("sell_none", lang))
            st.caption(t("sell_none_cap", lang))

    with st.container(border=True):
        card("location_on", "#0EA5E9", t("where_title", lang))
        top = pd.DataFrame()
        if district_data:
            dc = pd.DataFrame(district_data)
            top = dc[(dc["season"] == season) & (dc["crop"] == crop) & (dc["district_total_entries"] >= 100)]
            top = top.sort_values("share_of_entries", ascending=False).head(3)
        if top.empty:
            st.markdown(t("where_none", lang))
        else:
            st.markdown(" | ".join(f"**{i + 1}. {r['district']}** ({r['share_of_entries'] * 100:.0f}%)"
                                   for i, (_, r) in enumerate(top.iterrows())))
            st.caption(t("where_cap", lang, crop=name))
