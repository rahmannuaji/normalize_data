"""Satu-satunya pintu masuk dari browser (Pyodide): JSON string masuk, JSON string keluar."""
import functools
import json
import math

import numpy as np

from . import diagnose as dg, io, normality, prep, remedies, report as rp, target as tg

_S = {}
_NOT_LOADED = "Data belum dimuat. Masukkan data di langkah 1."


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    if isinstance(o, np.generic):
        o = o.item()
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o


def _dumps(o):
    return json.dumps(_clean(o), ensure_ascii=False)


def _endpoint(fn):
    @functools.wraps(fn)
    def run(payload="{}"):
        try:
            return _dumps(fn(**json.loads(payload)))
        except ValueError as e:  # termasuk GoalError
            return _dumps({"error": str(e)})
        except Exception as e:
            return _dumps({"error": f"Terjadi kesalahan tak terduga: {type(e).__name__}: {e}"})
    return run


def _need(key="raw"):
    if "raw" not in _S:
        raise ValueError(_NOT_LOADED)
    if key not in _S:
        raise ValueError("Atur variabel dulu di langkah 2." if key == "scores" else "Pilih tujuan analisis dan jalankan pengecekan dulu.")


def _work(transformed=True):
    """Skor setelah baris dikeluarkan, lalu (opsional) transformasi."""
    s = _S["scores"]
    if _S["excluded"]:
        s = remedies.exclude_rows(s, _S["excluded"])
    tr = _S["transform"]
    if transformed and tr:
        s = s.copy()
        for name in _transform_names():
            s[name] = remedies.transform(s[name], tr["method"])[0]
    return s


def _transform_names():
    only_y = _S["goal"] in ("regression", "ttest_ind", "ttest_paired", "anova")
    return [v["name"] for v in _S["variables"] if v["role"] == "Y" or not only_y]


def _checks(scores, transformed):
    out = []
    ranges = _S["info"]["score_range"]
    for t in tg.build_targets(scores, _S["variables"], _S["goal"]):
        c = normality.check_target(t, _S["goal"], _S["alpha"])
        y = t["y"] or t["label"]
        rng = None if transformed else ranges.get(y)
        yv = scores.loc[[r - 1 for r in t["rows"]], t["y"]].to_numpy() if t["kind"] == "residual" else t["values"]
        c["findings"] = dg.diagnose(t, c["moments"] or {}, rng, yv, _S["info"]["warnings"]) if c["moments"] else []
        out.append(c)
    return out


@_endpoint
def load_table(path, sheet=None):
    df, meta = io.read_table(path, sheet or None)
    _S.clear()
    _S.update(raw=df, fixes=[], excluded={}, transform=None, alternatives=[])
    return {**io.table_summary(df), **meta}


@_endpoint
def set_cell(row, column, value):
    _need()
    raw = _S["raw"]
    if column not in raw.columns or not 1 <= row <= len(raw):
        raise ValueError(f"Sel baris {row} kolom {column} tidak ada.")
    old = raw.at[row - 1, column]
    raw[column] = raw[column].astype(object)
    raw.at[row - 1, column] = value
    _S["fixes"].append({"row": row, "column": column, "old": None if old != old else old, "new": value})
    return {"ok": True}


@_endpoint
def prepare(variables, group=None):
    _need()
    scores, info = prep.build_scores(_S["raw"], variables, group or None)
    for k in ("goal", "alpha", "checks"):
        _S.pop(k, None)
    _S.update(variables=variables, group=group, scores=scores, info=info, excluded={}, transform=None, alternatives=[])
    prev = scores.head(10)
    return {**info, "preview": [{"row": int(i) + 1, **r} for i, r in zip(prev.index, prev.to_dict("records"))]}


@_endpoint
def check(goal, alpha=0.05):
    _need("scores")
    _S.update(goal=goal, alpha=alpha, excluded={}, transform=None, alternatives=[])
    _S["checks"] = _checks(_S["scores"], False)
    return {"targets": _S["checks"]}


@_endpoint
def remedy(kind, method=None, reasons=None):
    _need("scores")
    _need("checks")
    if kind == "alternative":
        _S["alternatives"] = remedies.alternative(_work(False), _S["variables"], _S["goal"])
        return _S["alternatives"]
    before = _checks(_work(), _S["transform"] is not None)
    if kind == "transform":
        # ponytail: info hanya dari variabel pertama; metode sama dipakai untuk semua variabel
        s = _S["scores"] if not _S["excluded"] else remedies.exclude_rows(_S["scores"], _S["excluded"])
        info = remedies.transform(s[_transform_names()[0]], method)[1]
        _S["transform"] = info
    elif kind == "exclude":
        ex = {int(r): k for r, k in reasons.items()}
        remedies.exclude_rows(_S["scores"], ex)  # validasi alasan/baris sebelum disimpan
        _S["excluded"] = ex
        info = None
    else:
        raise ValueError(f"Jenis perbaikan tidak dikenal: {kind}.")
    out = {"before": before, "after": _checks(_work(), _S["transform"] is not None)}
    return {"info": info, **out} if kind == "transform" else out


@_endpoint
def report(chosen_id=None):
    _need("scores")
    _need("checks")
    alts = _S["alternatives"]["alternatives"] if _S["alternatives"] else []
    chosen = next((a for a in alts if a["id"] == chosen_id), None) if chosen_id else None
    return rp.build_report({"goal": _S["goal"], "checks": _S["checks"], "fixes": _S["fixes"],
                            "excluded": _S["excluded"], "transform": _S["transform"], "chosen": chosen})
