import sys, json
d = sys.argv[1]
cal = json.load(open(f"{d}/harvest_calendar.json")); px = json.load(open(f"{d}/seasonal_price_index.json"))
MN = ["01 Jan","02 Feb","03 Mar","04 Apr","05 May","06 Jun","07 Jul","08 Aug","09 Sep","10 Oct","11 Nov","12 Dec"]
for r in cal:
    for k in ["price_index_at_harvest","best_month_within_3m","price_gain_hold_3m_pct","price_gain_hold_6m_pct","harvest_in_cheap_season"]:
        r[k] = None
    g = r.get("cpi_group")
    if g not in px: continue
    h = int(r["peak_approx_month"]) - 1
    idx = [px[g][m] for m in MN]
    def best(k):
        c = [(idx[(h + j) % 12], (h + j) % 12) for j in range(0, k + 1)]
        return max(c)
    b3, b6 = best(3), best(6)
    r["price_index_at_harvest"] = round(idx[h], 3)
    r["best_month_within_3m"] = MN[b3[1]]
    r["price_gain_hold_3m_pct"] = round((b3[0] / idx[h] - 1) * 100, 1)
    r["price_gain_hold_6m_pct"] = round((b6[0] / idx[h] - 1) * 100, 1)
    r["harvest_in_cheap_season"] = bool(idx[h] < 0.99)
json.dump(cal, open(f"{d}/harvest_calendar.json", "w"), indent=1)
rows = [r for r in cal if r["price_gain_hold_3m_pct"] is not None]
print("rows with price join:", len(rows), "of", len(cal))
print(f"{'crop':15}{'season':9}{'peak window':14}{'grp':8}{'conf':16}{'idx@h':>6}{'best3':>8}{'+3m%':>6}{'+6m%':>6}")
for r in sorted(rows, key=lambda r: -r["price_gain_hold_3m_pct"]):
    print(f"{r['crop']:15}{r['season'][-1]:9}{r['peak_harvest_window']:14}{r['cpi_group'][:7]:8}{r['cpi_mapping_confidence']:16}{r['price_index_at_harvest']:>6}{r['best_month_within_3m'][3:]:>8}{r['price_gain_hold_3m_pct']:>6}{r['price_gain_hold_6m_pct']:>6}")
