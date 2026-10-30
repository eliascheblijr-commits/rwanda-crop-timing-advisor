"""Simplified Farmer Assistant view (Tab 1). Premium Dark Native redesign."""
import pandas as pd
import streamlit as st
from components.state_manager import sync_crop, sync_season, get_active_index

def render(cal: pd.DataFrame, district_data: list):
    """Renders the simplified wizard interface natively."""
    
    st.markdown("## <span class='ph-bold ph-plant' style='color: #10B981;'></span> Farmer Assistant", unsafe_allow_html=True)
    st.markdown("<span style='color: #94A3B8;'>Select what you are growing and when to see optimal planting, harvesting, and selling times.</span>", unsafe_allow_html=True)
    st.markdown("---")

    c1, c2 = st.columns(2)
    
    all_crops = sorted(cal["crop"].unique())
    crop_idx = get_active_index(all_crops, "master_crop")
    
    crop = c1.selectbox(
        "Crop", 
        all_crops, 
        index=crop_idx, 
        key="wizard_crop",
        on_change=sync_crop,
        args=("wizard_crop",)
    )
    
    available_seasons = sorted(cal.loc[cal["crop"] == crop, "season"].unique())
    season_idx = get_active_index(available_seasons, "master_season")
    
    season = c2.selectbox(
        "Season", 
        available_seasons, 
        index=season_idx, 
        key="wizard_season",
        on_change=sync_season,
        args=("wizard_season",)
    )

    row = cal[(cal["crop"] == crop) & (cal["season"] == season)].iloc[0]
    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        sowing_window = row["peak_sowing_window"] if pd.notna(row["peak_sowing_window"]) else "an unspecified time"
        st.markdown(f"#### <span class='ph-bold ph-seedling' style='color: #0EA5E9;'></span> When to Plant", unsafe_allow_html=True)
        st.markdown(f"**Plant your seeds around {sowing_window}.**")
        st.caption("Most common planting period reported by farmers for this season.")

    with st.container(border=True):
        harvest_window = row["peak_harvest_window"] if pd.notna(row["peak_harvest_window"]) else "an unspecified time"
        st.markdown(f"#### <span class='ph-bold ph-basket' style='color: #10B981;'></span> When to Harvest", unsafe_allow_html=True)
        st.markdown(f"**Get ready to harvest around {harvest_window}.**")
        st.caption(f"Historically, {row['peak_window_share']:.0%} of plots are harvested during this window.")

    with st.container(border=True):
        st.markdown(f"#### <span class='ph-bold ph-coins' style='color: #FBBF24;'></span> When to Sell", unsafe_allow_html=True)
        if pd.notna(row.get("price_gain_hold_3m_pct")):
            if row["price_gain_hold_3m_pct"] > 0:
                st.markdown(f"**Hold your crop until {row['best_month_within_3m'][3:]} if you have safe storage.**")
                st.caption(f"Prices are usually lowest at harvest. Waiting up to 3 months historically returns +{row['price_gain_hold_3m_pct']:.1f}%.")
            else:
                st.markdown("**Sell immediately after harvest.**")
                st.caption("Historical prices show no benefit to storing this crop for later sale.")
        else:
            st.markdown("**Market prediction unavailable.**")
            st.caption("No historical consumer price tracking is available for this specific crop.")

    with st.container(border=True):
        st.markdown(f"#### <span class='ph-bold ph-map-pin' style='color: #0EA5E9;'></span> Top 3 Producing Districts", unsafe_allow_html=True)
        
        if district_data:
            dc = pd.DataFrame(district_data)
            sub = dc[(dc["season"] == season) & (dc["crop"] == crop)].dropna(subset=["share_of_entries"])
            
            if not sub.empty:
                top_districts = sub.sort_values("share_of_entries", ascending=False).head(3)
                ranking_str = " | ".join(
                    f"**{i+1}. {r['district']}** ({r['share_of_entries']*100:.0f}%)" 
                    for i, r in enumerate(top_districts.to_dict('records'))
                )
                st.markdown(ranking_str)
                st.caption("Based on the share of total surveyed plots for this crop and season.")
            else:
                st.markdown("Insufficient regional data for this crop and season.")
        else:
            st.markdown("District data is currently unavailable.")