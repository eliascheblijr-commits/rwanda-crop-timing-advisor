"""District x crop x season aggregates for the map (no household-level data).
Usage: python build_district.py <long.csv> <processed_dir>
Share = crop entries / all crop entries in that district and season. Yield median only where n >= 30."""
import sys, json, numpy as np, pandas as pd
src, outdir = sys.argv[1], sys.argv[2]
MIN_YIELD_N = 30
L = pd.read_csv(src, keep_default_na=False, na_values=[""])
cal = pd.DataFrame(json.load(open(f"{outdir}/harvest_calendar.json")))
keep = set(zip(cal.crop, cal.season))                      # same crop-season combinations as the calendar
area_ha = L.s2q2 * L.prop / 100 / 10000
L["yld"] = np.where((L.kg > 0) & (area_ha > 0), L.kg / area_ha, np.nan)
tot = L.groupby(["district", "Season"]).size().rename("total")
rows = []
for (d, s, c), g in L.groupby(["district", "Season", "crop"]):
    if (c, s) not in keep: continue
    y = g.yld.dropna()
    rows.append({"district": d, "season": s, "crop": c, "n_entries": int(len(g)),
                 "district_total_entries": int(tot[(d, s)]), "share_of_entries": round(len(g) / tot[(d, s)], 4), "n_yield": int(len(y)),
                 "yield_kg_per_ha_median": (round(float(y.median())) if len(y) >= MIN_YIELD_N else None)})
json.dump(rows, open(f"{outdir}/district_crop.json", "w"), indent=1)
D = pd.DataFrame(rows)
print("rows:", len(D), "| districts:", D.district.nunique(), "| min district-season total entries:", int(tot.min()))
print("rows with yield shown:", int(D.yield_kg_per_ha_median.notna().sum()), "of", len(D))
if "--report" in sys.argv:
    print("\nHow different are districts? (share of entries by district, Season A and B)")
    out = []
    for (s, c), g in D.groupby(["season", "crop"]):
        if len(g) >= 25 and g.n_entries.sum() >= 800:
            out.append({"season": s[-1], "crop": c, "districts": len(g), "min": g.share_of_entries.min(), "median": g.share_of_entries.median(),
                        "max": g.share_of_entries.max(), "max_over_median": round(g.share_of_entries.max() / g.share_of_entries.median(), 1),
                        "cv": round(g.share_of_entries.std() / g.share_of_entries.mean(), 2)})
    print(pd.DataFrame(out).sort_values("cv", ascending=False).round(3).to_string(index=False))
    # whole-mix similarity: cosine similarity of each district's crop mix with the national mix, Season A
    for s in ["Season A", "Season B"]:
        m = D[D.season == s].pivot_table(index="district", columns="crop", values="share_of_entries", fill_value=0)
        nat = m.mean()
        cos = m.apply(lambda r: float(np.dot(r, nat) / (np.linalg.norm(r) * np.linalg.norm(nat))), axis=1)
        print(f"\n{s}: cosine similarity of district crop mix to national mix: min {cos.min():.2f} (lowest: {cos.idxmin()}), median {cos.median():.2f}")
