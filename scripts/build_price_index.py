import sys, json, re, numpy as np, pandas as pd
xls, outdir = sys.argv[1], sys.argv[2]
a = pd.read_excel(xls, sheet_name="All Rwanda", header=None)
dates = pd.to_datetime(a.iloc[3, 4:], errors="coerce")
ok = dates.notna().values
ym = dates[ok].dt.to_period("M")
NAMES = {"Food and non-alcoholic beverages":"Food (all)","Bread and cereals":"Bread and cereals","Meat":"Meat",
         "Milk, cheese and eggs":"Milk, cheese and eggs","Vegetables":"Vegetables","Non-alcoholic beverages":"Non-alcoholic beverages",
         "GENERAL INDEX (CPI)":"General CPI"}
series = {}
for i in range(5, 24):
    lab = re.sub(r"^[v\xa0\s]+", "", str(a.iloc[i, 3])).strip()
    if lab in NAMES and a.iloc[i, 0] == 0 and a.iloc[i, 1] == 0:
        series[NAMES[lab]] = pd.Series(pd.to_numeric(a.iloc[i, 4:].values[ok], errors="coerce"), index=ym)
MN = ["01 Jan","02 Feb","03 Mar","04 Apr","05 May","06 Jun","07 Jul","08 Aug","09 Sep","10 Oct","11 Nov","12 Dec"]
def seasonal(s, start=None):
    s = s.dropna()
    # centered 2x12 moving average, then ratio to trend
    ma = s.rolling(12, center=True).mean().rolling(2).mean().shift(-1)
    r = (s / ma).dropna()
    if start: r = r[r.index >= pd.Period(start, "M")]
    df = pd.DataFrame({"r": r.values, "m": r.index.month, "y": r.index.year})
    g = df.groupby("m").r
    idx = g.mean(); idx = idx / idx.mean()
    sd = g.std(); n = g.count()
    above = df.assign(a=df.r > 1).groupby("m").a.mean()  # share of years above trend
    return idx, sd, n, above, df
out_idx, out_stats = {}, {}
for name, s in series.items():
    idx, sd, n, above, df = seasonal(s)
    idx15, *_ = seasonal(s, "2015-01")
    pk, tr = int(idx.idxmax()), int(idx.idxmin())
    # consistency: how often the peak month is above trend / trough below
    out_idx[name] = {MN[m-1]: round(float(idx[m]), 4) for m in range(1, 13)}
    out_stats[name] = {"peak_month": MN[pk-1], "trough_month": MN[tr-1],
        "amplitude_pct": round(float((idx.max()/idx.min()-1)*100), 1),
        "peak_above_trend_share_of_years": round(float(above[pk]), 2),
        "trough_below_trend_share_of_years": round(float(1-above[tr]), 2),
        "years_per_month": int(n.min()), "avg_sd_across_years": round(float(sd.mean()), 4),
        "corr_full_vs_2015plus": round(float(np.corrcoef(idx.values, idx15.values)[0, 1]), 2),
        "first_obs": str(s.dropna().index.min()), "last_obs": str(s.dropna().index.max())}
KEEP = ["Bread and cereals", "Vegetables", "Food (all)"]  # other groups show <3% seasonality, kept in stats only
json.dump({k: v for k, v in out_idx.items() if k in KEEP}, open(f"{outdir}/seasonal_price_index.json", "w"), indent=1)
json.dump(out_stats, open(f"{outdir}/seasonal_price_stats.json", "w"), indent=1)
print(pd.DataFrame(out_stats).T.to_string())
print()
print(pd.DataFrame(out_idx).round(3).to_string())
