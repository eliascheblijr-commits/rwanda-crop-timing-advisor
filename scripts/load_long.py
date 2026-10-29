import sys, glob, pandas as pd
src, out = sys.argv[1], sys.argv[2]
f = glob.glob(src + "/AHS2024_Section3_4*")[0]
cols = ["district","Season","s2q1","s2q2"]
for k in range(1,8):
    suf = f"_{k}"
    cols += [f"s3_q4{suf}", f"s3_q4{suf}a", f"s3_q7{suf}", f"s3_q8{suf}", f"s3_q20{suf}"]
with pd.io.stata.StataReader(f, convert_categoricals=False) as r:
    vl = r.value_labels(); vmap = dict(zip(r._varlist, r._lbllist))
    avail = set(r._varlist)
    cols = [c for c in cols if c in avail]
    d = r.read(columns=cols)
def dec(series, col):
    m = vl.get(vmap.get(col, ""), {})
    return series.map(m).where(series.map(m).notna(), series.astype(str))
rows = []
for k in range(1,8):
    s = f"_{k}"
    need = [f"s3_q4{s}", f"s3_q8{s}", f"s3_q20{s}"]
    if not all(c in d.columns for c in need): continue
    t = d[["district","Season","s2q1","s2q2"]].copy()
    t["crop"] = dec(d[f"s3_q4{s}"], f"s3_q4{s}")
    t["prop"] = d.get(f"s3_q4{s}a")
    t["sow"] = dec(d[f"s3_q7{s}"], f"s3_q7{s}") if f"s3_q7{s}" in d.columns else None
    t["window"] = dec(d[f"s3_q8{s}"], f"s3_q8{s}")
    t["kg"] = d[f"s3_q20{s}"]
    t["slot"] = k
    t = t[d[f"s3_q4{s}"].notna()]
    rows.append(t)
L = pd.concat(rows, ignore_index=True)
for col in ["district","Season"]:
    L[col] = dec(L[col], col)
L.to_csv(out, index=False)
print("long rows:", len(L), "| crops:", L.crop.nunique(), "| seasons:", L.Season.value_counts().to_dict())
print("kg non-null:", int(L.kg.notna().sum()), "| kg<=0:", int((L.kg<=0).sum()), "| kg describe:", L.kg.describe(percentiles=[.5,.99]).round(1).to_dict())
print("prop non-null:", int(L.prop.notna().sum()), "| area_sqm non-null:", int(L.s2q2.notna().sum()))
print("\nWINDOW LABELS:"); print(L.window.value_counts().to_string())
