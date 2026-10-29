# Rwanda Crop Timing Advisor

NISR 2026 Big Data Hackathon, Track 1 (Agriculture).

**Status: working app with four tabs (crop explorer, crop ranking, district map, price outlook) built from AHS 2024 (27 crops, 63 crop-season combinations, 30 districts) and the NISR CPI to September 2026. 43 of the 63 combinations have a price pattern; the rest are crops with no CPI group.**

## Main findings
- **Vegetable prices are strongly seasonal**: about 7% above trend in October and 8% below in January (16% swing). The January trough is below trend in every year since 2009, and the pattern holds using only 2015 onward.
- **Cereal prices are only weakly seasonal** (about 5% swing, lowest in August, highest in December), so holding maize or sorghum rarely pays at the index level.
- **Meat, dairy and beverages show under 3% seasonality** and are not used.
- For vegetable-group crops harvested in cheap months, the price index typically rises 4-10% within 3 months, before storage costs and losses.

- **Districts differ in what they grow, not only in climate**: Irish potato is under 1% of crop entries in many districts but up to 19.6% in the north-west (median 1.3%); climbing bean ranges from 0.2% to 37%. Shown on the district map (unweighted sample shares).
- **Price forecasts have modest skill**: over 29 rolling backtests (2019-2026, 1-6 months ahead), the best model beats a "no change" forecast by about 20% for food overall (typical error 4.6%), 15% for cereals and 24% for vegetables (typical error 7.4%). The forecast for late 2026 follows a sharp September rise, and the models disagree by about 7% by March 2027, so treat it as a range, not a point.

## What it does
Helps farmers and district agriculture officers see **when each crop is harvested, how consumer prices for that crop group usually behave in those months, and where harvest and price timing is mismatched**. The goal is better decisions on crop choice per season and on when to sell or store.

## Data used
| Source | What we use it for |
|---|---|
| NISR Agricultural Household Survey (AHS) 2024 | Crop harvest windows, sowing dates, harvest quantities, seasons A/B/C, district; fruit sales and farm-gate prices |
| NISR Consumer Price Index time series (to Sep 2026) | Monthly price indices by food group (cereals, vegetables, meat, dairy, beverages) to build a seasonal price index |

Details and variable mapping: [`data/data_dictionary.json`](data/data_dictionary.json).

**Raw microdata is not redistributed here.** Download it from the NISR microdata portal (https://microdata.statistics.gov.rw) after registering. This repo contains only aggregated, non-household-level tables in `data/processed/`.

## How to use the app
1. **Crop explorer**: pick a crop and season to see harvest windows, yield range, the seasonal price pattern of its CPI group with the harvest month marked, and the typical gain from holding 3 or 6 months.
2. **Compare crops**: rank all crops in a season by gain from holding, or by how cheap the harvest month is. Ties occur because crops in one CPI group share a price pattern.
3. **District map**: choose a season and crop to see its share of crop entries, or median yield, by district. Districts with fewer than 100 entries (most of Season C) are greyed out.
4. **Price outlook**: 6-month forecast with an 80% range for cereals, vegetables and all food, with the other candidate models shown dotted and the backtest error stated.

## Method
1. Build a harvest-window calendar per crop and season from AHS.
2. Remove the inflation trend from CPI by dividing each month by its 12-month average, then average by calendar month to get a seasonal price index per food group.
3. Map AHS crops to CPI food groups and compute a sell-timing gap.
4. Compute each crop's share of entries and median yield by district (yield only where n >= 30).
5. Forecast the CPI groups on the log index with four models (naive, seasonal naive with annual drift, damped-trend ETS, SARIMA(0,1,1)(0,1,1)12). Pick the best per group by average MAPE over a rolling-origin backtest (29 origins, horizons 1-6). The 80% ranges come from backtest error quantiles. The model is chosen on the same backtest it is scored on, so skill is slightly optimistic.

## Limitations
- AHS 2024 covers one year, so yield and timing results are descriptive, not forecasts.
- CPI is a consumer price index, not a farm-gate price. Fruit farm-gate prices from AHS are used as a cross-check where available.
- CPI food data is published by group, not by single crop. The crop-to-group mapping is an assumption and is documented.
- Survey weights have not been verified for all seasons. Counts are sample figures unless stated.
- Tea is not in the AHS crop list.
- Seasonal price patterns are for the whole CPI food group, so crops in the same group differ only by harvest timing.
- Beans, potatoes, cassava, sweet potato, taro and cooking banana are assumed to follow the Vegetables group; this is unverified and flagged in the app.
- The "gain from holding" is a change in a consumer price index. It ignores storage costs, post-harvest losses and farm-gate margins, none of which the survey measures.
- Open-ended harvest windows (Before X, After Y) use an approximate month.

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```

## Rebuild the processed tables (optional)
Needs the raw AHS 2024 `.dta` files from the NISR portal in a local folder:
```
python scripts/load_long.py <folder_with_dta_files> long.csv
python scripts/build_calendar.py long.csv data/processed
python scripts/build_price_index.py <CPI_time_series_September_2026.xls> data/processed
python scripts/build_sell_timing.py data/processed
python scripts/build_district.py long.csv data/processed
python scripts/build_forecast.py <CPI_time_series_September_2026.xls> data/processed
```
The committed `data/processed/` files are already the output of these steps.

## Credits
District boundaries: geoBoundaries (CC BY 4.0), https://www.geoboundaries.org. Runfola et al. (2020), "geoBoundaries: A global database of political administrative boundaries", PLoS ONE 15(4): e0231866. Source boundaries attributed to NISR. Simplified and saved as `data/districts.geojson`.

## Alignment
NST2 and PSTA5 (agriculture transformation). To be completed.

## Team
To be completed (two members, at least one Rwandan citizen).

## Repository layout
```
README.md
app.py
requirements.txt
scripts/         code that builds data/processed/ from the raw NISR files
data/            data used, dictionary, processed tables, districts.geojson
demo/            screen-recorded demo (max 3 minutes)
student_cards/   eligibility documents
```
