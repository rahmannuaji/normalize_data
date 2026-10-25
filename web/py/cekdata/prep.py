import pandas as pd


def _num(x):
    return int(x) if float(x).is_integer() else float(x)


def _infer_scale(vals):
    v = pd.Series(vals.to_numpy().ravel()).dropna()
    keep = v.value_counts()[lambda c: c >= 0.01 * len(v)].index
    return (keep.min(), keep.max()) if len(keep) else None


def build_scores(df, variables, group=None):
    cols = list(dict.fromkeys(c for v in variables for c in v["columns"]))
    raw = df[cols]
    num = raw.apply(pd.to_numeric, errors="coerce")
    warnings = []
    for c in cols:
        n = int((num[c].isna() & raw[c].notna()).sum())
        if n:
            warnings.append({"kind": "non_numeric", "column": c, "count": n})

    ok = num.notna().all(axis=1)
    if group:
        ok &= df[group].notna()
    dropped = [int(i) + 1 for i in df.index[~ok]]
    num = num[ok]

    scores, ranges = pd.DataFrame(index=num.index), {}
    for v in variables:
        cs, k = v["columns"], len(v["columns"])
        items = num[cs]
        scale = v["scale"] if v["scale"] else (_infer_scale(items) if k >= 2 else None)
        if scale:
            lo, hi = scale
            for c in cs:
                for i in items.index[(items[c] < lo) | (items[c] > hi)]:
                    warnings.append({"kind": "out_of_range", "row": int(i) + 1, "column": c, "value": float(items.at[i, c])})
            items = items.copy()
            for c in v["reversed"]:
                items[c] = lo + hi - items[c]
        if k >= 2:
            for c in cs:
                r = items[c].corr(items.drop(columns=c).sum(axis=1))
                if pd.notna(r) and r < 0:
                    warnings.append({"kind": "negative_item_total", "variable": v["name"], "item": c, "r": round(float(r), 2)})
        scores[v["name"]] = items.sum(axis=1) if v["combine"] == "sum" else items.mean(axis=1)
        ranges[v["name"]] = None if not scale else (
            [_num(k * lo), _num(k * hi)] if v["combine"] == "sum" else [_num(lo), _num(hi)])
    if group:
        scores["__group"] = df.loc[num.index, group]
    info = {"n_used": len(scores), "n_dropped": len(dropped), "dropped_rows": dropped,
            "warnings": warnings, "score_range": ranges}
    return scores, info
