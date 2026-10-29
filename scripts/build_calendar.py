import sys, re, json, pandas as pd, numpy as np
src, outdir = sys.argv[1], sys.argv[2]
L = pd.read_csv(src, keep_default_na=False, na_values=[""])
MON = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
def norm(s): return re.sub(r"\s+","",str(s)).lower()
# (order, label, approx_month) per season; open-ended windows are approximations
W = {
 "Season A": {"before01/12":(1,"Before 1 Dec",11),"between01-15/12":(2,"1-15 Dec",12),"between16-31/12":(3,"16-31 Dec",12),
              "between01-15/01":(4,"1-15 Jan",1),"between16-31/01":(5,"16-31 Jan",1),"between01-28/02":(6,"1-28 Feb",2),"afterfeb":(7,"After Feb",3)},
 "Season B": {"before01/05":(1,"Before 1 May",4),"between01-15/05":(2,"1-15 May",5),"between15-31/05":(3,"15-31 May",5),
              "between01-15/06":(4,"1-15 Jun",6),"between16-30/06":(5,"16-30 Jun",6),"between01-15/07":(6,"1-15 Jul",7),
              "between16-31/07":(7,"16-31 Jul",7),"between01-31/08":(8,"1-31 Aug",8),"afteraugust":(9,"After Aug",9)},
 "Season C": {"before01/08":(1,"Before 1 Aug",7),"between01-15/08":(2,"1-15 Aug",8),"between16-31/08":(3,"16-31 Aug",8),
              "between01-15/09":(4,"1-15 Sep",9),"between16-30/09":(5,"16-30 Sep",9),"after30/09":(6,"After 30 Sep",10)},
}
def hwin(r):
    return W[r.Season].get(norm(r.window))
L["h"] = [hwin(r) for r in L.itertuples()]
L["has_win"] = L.h.notna()
def sow(s):
    t = str(s); m = re.search(r"between\D*(\d+)\D+(\d+)\s*/\s*(\d+)", t, re.I)
    if m: return f"{int(m[1])}-{int(m[2])} {MON[int(m[3])]}"
    m = re.search(r"(after|before)\s*(\d+)\s*/\s*(\d+)", t, re.I)
    if m: return f"{m[1].capitalize()} {int(m[2])} {MON[int(m[3])]}"
    return None
L["sow_l"] = L.sow.map(sow)
area_ha = L.s2q2 * L.prop / 100 / 10000
L["yld"] = np.where((L.kg > 0) & (area_ha > 0), L.kg / area_ha, np.nan)
MAP = {  # draft, flagged in output
 "Maize":("Bread and cereals","assumed"),"Sorghum":("Bread and cereals","assumed"),"Paddy rice":("Bread and cereals","assumed"),"Wheat":("Bread and cereals","assumed"),
 "Tomato":("Vegetables","assumed"),"Onion":("Vegetables","assumed"),"Cabbage":("Vegetables","assumed"),"Carrot":("Vegetables","assumed"),
 "Eggplant":("Vegetables","assumed"),"Amaranth":("Vegetables","assumed"),
 "Climbing bean":("Vegetables","probable_verify"),"Bush bean":("Vegetables","probable_verify"),"Irish potato":("Vegetables","probable_verify"),
 "Sweet potato":("Vegetables","probable_verify"),"Cassava":("Vegetables","probable_verify"),"Taro":("Vegetables","probable_verify"),
 "Cooking banana":("Vegetables","probable_verify"),
}
MIN_N = 30
flat, long = [], []
dropped = 0
for (crop, season), g in L.groupby(["crop","Season"]):
    n_all = len(g); gw = g[g.has_win]
    if len(gw) < MIN_N: dropped += 1; continue
    shares = gw.h.map(lambda x: x[1]).value_counts()
    order = {x[1]: x[0] for x in W[season].values()}; mon = {x[1]: x[2] for x in W[season].values()}
    for lab, c in shares.items():
        long.append({"crop":crop,"season":season,"window":lab,"order":order[lab],"approx_month":mon[lab],"share":round(c/len(gw),3),"n":int(c)})
    peak = shares.idxmax()
    y = g.yld.dropna(); sw = g.sow_l.dropna()
    cg, conf = MAP.get(crop, (None, "unmapped"))
    flat.append({"crop":crop,"season":season,"n_entries":int(n_all),"n_with_harvest_window":int(len(gw)),
        "share_window_unspecified":round(1-len(gw)/n_all,3),"peak_harvest_window":peak,"peak_window_share":round(shares.max()/len(gw),3),
        "peak_approx_month":mon[peak],"peak_sowing_window":(sw.value_counts().idxmax() if len(sw)>=MIN_N else None),
        "n_yield":int(len(y)),"yield_kg_per_ha_median":(round(float(y.median())) if len(y)>=MIN_N else None),
        "yield_kg_per_ha_p25":(round(float(y.quantile(.25))) if len(y)>=MIN_N else None),
        "yield_kg_per_ha_p75":(round(float(y.quantile(.75))) if len(y)>=MIN_N else None),
        "cpi_group":cg,"cpi_mapping_confidence":conf})
json.dump(flat, open(f"{outdir}/harvest_calendar.json","w"), indent=1)
json.dump(long, open(f"{outdir}/harvest_windows.json","w"), indent=1)
F = pd.DataFrame(flat)
print("flat rows:",len(F),"| long rows:",len(long),"| crop-season combos dropped (n<30):",dropped)
print("crops kept:",F.crop.nunique(),"| per season:",F.season.value_counts().to_dict())
print("window parse rate overall: %.1f%% (rest = 'Other season'/junk)" % (100*L.has_win.mean()))
show=F[F.crop.isin(["Maize","Climbing bean","Bush bean","Irish potato","Sweet potato","Cassava","Sorghum","Tomato","Soybean","Coffee","Cooking banana"])]
print(show[["crop","season","n_entries","share_window_unspecified","peak_harvest_window","peak_window_share","peak_sowing_window","yield_kg_per_ha_median","yield_kg_per_ha_p25","yield_kg_per_ha_p75"]].to_string(index=False))
