# Data

- `data_dictionary.json` - sources, variables used, processing rules, and what is unverified.
- `processed/` - aggregated tables produced from the sources (no household-level records, no household IDs).
  - `harvest_calendar.json` - one row per crop x season: peak harvest and sowing windows, yield summary, CPI group, price timing
  - `harvest_windows.json` - share of plots by harvest window per crop x season (for the bar chart)
  - `seasonal_price_index.json` - month-of-year price index for the CPI groups used by the app
  - `seasonal_price_stats.json` - peak/trough, amplitude and stability checks for every CPI food group
  - `district_crop.json` - per district x season x crop: share of crop entries, entry counts, median yield (n >= 30)
  - `price_forecast.json` - 6-month forecasts with 80% ranges, alternative models, history and backtest scores per CPI group
- `districts.geojson` - simplified district boundaries from geoBoundaries (CC BY 4.0, https://www.geoboundaries.org), source NISR

Raw microdata and the raw CPI workbook are NOT stored here. Links:
- AHS 2024 and other NISR microdata: https://microdata.statistics.gov.rw
- CPI time series: https://statistics.gov.rw/node/1836

The raw files are too large (the AHS crop file is about 129 MB) and are subject to the NISR portal terms of use.
