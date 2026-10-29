"""6-month-ahead forecasts of CPI food-group indices with a rolling-origin backtest.
Usage: python build_forecast.py <CPI_time_series.xls> <processed_dir>
Models (on log index): naive, seasonal naive + annual drift, damped-trend ETS, SARIMA(0,1,1)(0,1,1)12.
The model with the lowest average backtest error is used; 80% bands come from its backtest errors."""
import sys, re, json, warnings, numpy as np, pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
warnings.filterwarnings("ignore")
xls, outdir = sys.argv[1], sys.argv[2]
H, STEP, FIRST = 6, 3, "2019-01"
a = pd.read_excel(xls, sheet_name="All Rwanda", header=None)
dates = pd.to_datetime(a.iloc[3, 4:], errors="coerce"); ok = dates.notna().values
ym = dates[ok].dt.to_period("M")
NAMES = {"Food and non-alcoholic beverages": "Food (all)", "Bread and cereals": "Bread and cereals", "Vegetables": "Vegetables"}
S = {}
for i in range(5, 24):
    lab = re.sub(r"^[v\xa0\s]+", "", str(a.iloc[i, 3])).strip()
    if lab in NAMES and a.iloc[i, 0] == 0 and a.iloc[i, 1] == 0:
        s = pd.Series(pd.to_numeric(a.iloc[i, 4:].values[ok], errors="coerce"), index=ym).dropna()
        S[NAMES[lab]] = s
def f_naive(y): return np.repeat(y[-1], H)
def f_snd(y): return np.array([y[len(y) - 12 + h - 1] + (y[-1] - y[-13]) for h in range(1, H + 1)])
def f_ets(y): return np.asarray(ExponentialSmoothing(y, trend="add", damped_trend=True, seasonal="add", seasonal_periods=12,
                                                    initialization_method="estimated").fit().forecast(H))
def f_sarima(y): return np.asarray(SARIMAX(y, order=(0, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False, maxiter=60).forecast(H))
MODELS = {"naive (last value)": f_naive, "seasonal naive + annual drift": f_snd, "damped-trend ETS": f_ets, "SARIMA(0,1,1)(0,1,1)12": f_sarima}
result = {}
for name, s in S.items():
    # the CPI sheet must be one continuous monthly series
    assert (np.diff(s.index.asi8) == 1).all(), f"gap in {name}"
    y = np.log(s.values); idx = s.index
    first = int(np.where(idx == pd.Period(FIRST, "M"))[0][0]); last_origin = len(y) - 1 - H
    origins = list(range(first, last_origin + 1, STEP))
    err = {m: {h: [] for h in range(1, H + 1)} for m in MODELS}   # signed log errors, forecast - actual
    for p in origins:
        tr = y[:p + 1]
        for m, f in MODELS.items():
            try: fc = f(tr)
            except Exception: continue
            for h in range(1, H + 1): err[m][h].append(fc[h - 1] - y[p + h])
    mape = {m: {h: round(float(np.mean(np.abs(np.expm1(err[m][h])))) * 100, 2) for h in (1, 3, 6)} for m in MODELS}
    avg = {m: np.mean([np.mean(np.abs(np.expm1(err[m][h]))) for h in range(1, H + 1)]) * 100 for m in MODELS}
    best = min(avg, key=avg.get)
    skill = round((avg["naive (last value)"] - avg[best]) / avg["naive (last value)"] * 100, 1)
    fc = MODELS[best](y)
    alt = {m: [round(float(np.exp(v)), 1) for v in f(y)] for m, f in MODELS.items()}
    q = {h: (np.quantile(err[best][h], 0.1), np.quantile(err[best][h], 0.9)) for h in range(1, H + 1)}  # bands from backtest errors
    last = idx[-1]
    fcst = []
    for h in range(1, H + 1):
        mth = last + h
        lo, hi = np.exp(fc[h - 1] - q[h][1]), np.exp(fc[h - 1] - q[h][0])
        yoy = np.exp(fc[h - 1]) / s.values[len(s) - 12 + h - 1] - 1 if h <= 12 else None
        fcst.append({"month": str(mth), "value": round(float(np.exp(fc[h - 1])), 1), "lo80": round(float(lo), 1), "hi80": round(float(hi), 1),
                     "yoy_pct": round(float(yoy) * 100, 1)})
    hist = [{"month": str(i), "value": round(float(v), 1)} for i, v in zip(idx[-36:], s.values[-36:])]
    result[name] = {"model": best, "alternatives": alt, "last_observed": str(last), "history": hist, "forecast": fcst,
        "backtest": {"origins": len(origins), "first_origin": str(idx[origins[0]]), "last_origin": str(idx[origins[-1]]), "horizons_months": H,
                     "mape_pct": mape, "avg_mape_1_to_6_pct": {m: round(float(v), 2) for m, v in avg.items()},
                     "skill_vs_naive_pct": skill, "note": "Model chosen on the same backtest it is scored on, so skill is slightly optimistic."}}
    print(f"\n{name}: {len(origins)} origins ({idx[origins[0]]} to {idx[origins[-1]]}) | best = {best} | skill vs naive = {skill}%")
    print(pd.DataFrame(mape).T.rename(columns={1: "h=1", 3: "h=3", 6: "h=6"}).assign(avg_1to6=pd.Series(avg).round(2)).to_string())
    print("forecast:", [(f["month"], f["value"], f["lo80"], f["hi80"]) for f in fcst][:6])
import os; os.makedirs(outdir, exist_ok=True)
json.dump(result, open(f"{outdir}/price_forecast.json", "w"), indent=1)
