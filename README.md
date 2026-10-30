# Rwanda Crop Timing Advisor

**Know when to plant, when to harvest, and when to sell.** Built from NISR data for the 2026 NISR Big Data Hackathon, Track 1 (Agriculture).

- **Live app:** https://rwanda-crop-timing-advisor.streamlit.app/
- **Demo video (2:13 min):** https://youtu.be/W5AKKv2Oluo?si=z5Ie78FBY16B77R8, or see `demo/`_

---

## 1. Why: the problem

Farmers in the same area tend to plant and harvest at the same time, so their crops reach the market together. Our price data shows this matters: for vegetables, prices are lowest around harvest and rise afterwards. A farmer who needs cash and sells straight away can miss that rise.

Farmers and district agriculture officers rarely have a simple answer to three questions:

1. **When do farmers like me usually plant and harvest this crop?**
2. **Is the harvest month a cheap month for this crop's prices, and is waiting worth it?**
3. **Where is this crop already common, and how does that differ from district to district?**

NISR already collects the data that answers these questions. It sits in survey files and spreadsheets that a farmer or an extension officer will not open. This project turns it into a tool that gives plain answers.

## 2. What: the app

A web app with five pages. The first is written for farmers, and the rest give officers and analysts the detail behind it.

| Page | Who it is for | What it shows |
|---|---|---|
| **My crop** | Farmers, extension agents | Pick a crop and a season. Get four short answers: when to plant, when to harvest, when to sell, and where it is most common. |
| **Crop details** | Officers | Harvest timing chart, the price pattern through the year with the harvest month marked, typical harvest per hectare. |
| **Compare crops** | Officers, planners | Rank all crops in a season by how much waiting could gain, or by how cheap the harvest month is. |
| **Where it grows** | District officers | A map of how common a crop is in each of the 30 districts, or its typical harvest per hectare. |
| **Price forecast** | Officers, analysts | A six-month price forecast with a likely range, and a statement of how accurate past forecasts were. |

**What the data shows:**

- **Vegetable prices follow a strong yearly cycle.** They run about 7% above the yearly trend in October and about 8% below it in January, a swing of about 16%. January is below trend in every year since 2009, and the pattern holds when only 2015 onward is used.
- **For vegetable-group crops harvested in cheap months, waiting up to 3 months raises the price index by about 4% to 10%** (median 6.5% across 12 crop-season cases). This is before storage costs and losses.
- **Grain prices are only weakly seasonal** (about a 5% swing). For maize and sorghum, the app says plainly that waiting rarely pays.
- **Districts are not alike in what they grow.** Irish potato is under 1% of crops grown in many districts but up to 19.6% in the north-west. Climbing bean ranges from 0.2% to 37%.
- **Price forecasts beat "nothing will change", but not by a lot.** Tested on 29 past forecasts (2019 to 2026, 1 to 6 months ahead), the chosen model was about 20% more accurate for food overall, 15% for cereals, and 24% for vegetables. Typical error was 4.6% for food and 7.4% for vegetables.

## 3. How to use it

**As a farmer or extension agent**
1. Open **My crop**.
2. Under "What do you grow?", choose your crop.
3. Under "Which growing season?", choose the season. Each season is labelled with its months:

   | Season | Planting | Harvest |
   |---|---|---|
   | Season A | around September | December to February |
   | Season B | February to March | May to August |
   | Season C | June to July | August to September |

   These months come from the survey's own planting and harvest answers.
4. Read the four cards. The "When to sell" card tells you whether waiting is likely to pay and which month is usually best.

**As an officer or analyst**
- Use **Compare crops** to see which crops have the most to gain from storage in a season.
- Use **Where it grows** to see regional differences before planning training or storage support.
- Use **Price forecast** to see where food prices are heading, and how far to trust it.

Choosing a crop on one page carries over to the others.

## 4. How it works

**Data**

| Source | Used for |
|---|---|
| NISR Agricultural Household Survey (AHS) 2024 | When each crop is planted and harvested, yields, and which districts grow what (14 files, 30 districts, Seasons A, B and C) |
| NISR Consumer Price Index (CPI), February 2009 to September 2026 | Monthly food prices, to find each year's price cycle and to forecast |
| geoBoundaries (CC BY 4.0) | District outlines for the map |

**Method**
1. From the survey, build a harvest and planting calendar per crop and season. Open-ended answers such as "Before 1 Dec" are given an approximate month.
2. From the CPI, remove the long-run rise in prices by dividing each month by its centred 12-month average. Average the result by calendar month to get a seasonal price pattern per food group.
3. Match each crop to a CPI food group and work out the price in the harvest month, the best month within 3 and 6 months, and the gain from waiting.
4. For each district, work out how common each crop is, and its typical harvest per hectare where there are at least 30 records.
5. Forecast with four standard models on the log of the index. Test each on 29 rolling past forecasts and keep the most accurate per group. The "likely range" comes from the size of past errors.

Every step is a script in `scripts/`, so the results can be reproduced.

## 5. Keeping it current: how the system handles future data

**Today (honest status).** The data files in `data/processed/` are built once from the 2024 survey and the September 2026 price file. The app does not fetch anything live. It reads these files and shows "prices up to September 2026" in the sidebar, which it takes from the data itself. Nothing is hard-coded, so refreshed files update the label.

**Why not "live" data.** NISR publishes the CPI once a month and the household survey about once a year. The right design is a reliable monthly refresh, not a live stream.

**The design**

1. **Separate data from app.** The app only reads the files in `data/processed/`. Refreshing means producing new files and publishing them. The app code does not change.
2. **Rebuild with the same scripts.** Every file comes from a script in `scripts/` that takes the raw file and an output folder as inputs. A new CPI release is rebuilt by running the same two commands (seasonal pattern and forecast).
3. **Monthly scheduled job (planned).** A scheduled GitHub Actions job will download the newest CPI file, run the rebuild, run the checks in step 4, and commit the new files, which redeploys the app. NISR offers the CPI as a downloadable spreadsheet, not an API, so the job needs a fixed download address and may need a manual update if NISR changes the page.
4. **Checks before publishing (planned).** The job will refuse to publish and keep the previous data if the file is missing a column, has a gap in months, has an implausible jump, or the forecast backtest gets much worse than before.
5. **Re-test the forecast each time.** Every refresh re-runs the rolling backtest, so the accuracy figure shown always matches the data it was computed from.
6. **New survey rounds.** When NISR releases a new AHS round, the same scripts rebuild the calendar and district tables. Several years can then be compared, which also shows how stable each crop's timing is.
7. **Better price data.** The largest step up in accuracy would be farm-gate and market prices by crop and district, instead of national food-group prices. The pipeline above is built to take such a source as one more input file.
8. **Reaching farmers without a smartphone.** The same answer cards can be sent by SMS or USSD, and shown in Kinyarwanda. The data files are small enough to be cached for offline use.

## 6. Limits

We would rather state these than have them found:

- **One survey year (2024).** Timing and yield results describe that year. They are not forecasts, and one year cannot show how much timing varies.
- **Consumer prices, not farm-gate prices.** The price pattern is from the CPI. What a farmer is actually paid will differ. The "gain from waiting" does not include storage costs, crop losses or the farmer's cash needs.
- **Prices are by food group, not by crop.** The CPI summary does not give separate series for maize, beans or potatoes. All crops in a group share one pattern. Beans, potatoes, cassava, sweet potato, taro and cooking banana are assumed to follow the vegetable group. This is our estimate and has not been confirmed against NISR's CPI methodology. The app marks these crops.
- **Survey counts are not weighted.** We have not confirmed that the survey weights are valid for all seasons, so the figures describe the sample, not the whole country. District figures from small samples can be noisy, and Season C has under 100 records in 25 of 30 districts.
- **Forecasts are modest.** They follow recent trends, and prices jumped about 9% in September 2026, so models differ by about 7% by March 2027. The app shows other models and the range. The model was chosen on the same tests it is scored on, so its accuracy is slightly flattering.
- **Which index.** The app uses the all-Rwanda CPI. NISR's headline inflation figures are for the urban index, so numbers differ. Rural food prices have risen faster than the national average.
- **Not covered.** Tea is not in the survey crop list. Avocado and macadamia are not in the crop file used here.

## 7. Alignment with national priorities

The app supports the agriculture transformation goals in **NST2** and **PSTA5**: helping smallholders earn more from the crops they already grow, through better market timing and post-harvest decisions, and giving district officers evidence for planning storage and training. It is built entirely on NISR data, and works with the official release schedule of that data.

## 8. Team

Elias Mario Chebli - Lead Developer
Irakoze Prince - Team Leader

## Run it yourself

```
pip install -r requirements.txt
streamlit run app.py
```

### Rebuild the data (optional)

Needs the raw AHS 2024 `.dta` files from the NISR microdata portal (free registration):
```
python scripts/load_long.py <folder_with_dta_files> long.csv
python scripts/build_calendar.py long.csv data/processed
python scripts/build_price_index.py <CPI_time_series_September_2026.xls> data/processed
python scripts/build_sell_timing.py data/processed
python scripts/build_district.py long.csv data/processed
python scripts/build_forecast.py <CPI_time_series_September_2026.xls> data/processed
```
The files already in `data/processed/` are the output of these steps. Raw microdata is not redistributed here, and no household-level records are in this repository. See `data/data_dictionary.json` for variables and processing rules.

## Repository layout
```
README.md             this document
app.py                the app: page, style and navigation
components/           the five pages and shared wording helpers
scripts/              builds data/processed/ from the raw NISR files
data/                 data dictionary, processed tables, district map outlines
demo/                 screen-recorded demo (max 3 minutes)
student_cards/        eligibility documents
.streamlit/           theme
```

## Credits and sources
- NISR Agricultural Household Survey 2024 (https://microdata.statistics.gov.rw) and NISR Consumer Price Index (https://statistics.gov.rw/node/1836).
- District boundaries: geoBoundaries (CC BY 4.0), https://www.geoboundaries.org. Runfola et al. (2020), "geoBoundaries: A global database of political administrative boundaries", PLoS ONE 15(4): e0231866.
