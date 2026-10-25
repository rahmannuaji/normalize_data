"""Satu-satunya pintu masuk dari browser (Pyodide): JSON string masuk, JSON string keluar."""
import datetime
import functools
import json
import math

import numpy as np
import pandas as pd

from . import diagnose as dg, io, normality, prep, remedies, report as rp, target as tg

_S = {}
_NOT_LOADED = "Data belum dimuat. Masukkan data di langkah 1."
_BLANK = "kosong"


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, np.ndarray):
        return _clean(o.tolist())
    if isinstance(o, np.generic):
        o = o.item()
    if o is pd.NaT:
        return None
    if isinstance(o, (datetime.date, datetime.datetime)):  # Timestamp turunan datetime
        return o.isoformat()
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


def _excluded_scores():
    s = _S["scores"]
    return remedies.exclude_rows(s, _S["excluded"]) if _S["excluded"] else s


def _work(transformed=True):
    """Skor setelah baris dikeluarkan, lalu (opsional) transformasi per variabel."""
    s = _excluded_scores()
    if transformed and _S["transform"]:
        s = s.copy()
        for name, info in _S["transform"].items():
            s[name] = remedies.transform(s[name], info["method"])[0]
    return s


def _transform_names():
    only_y = _S["goal"] in ("regression", "ttest_ind", "ttest_paired", "anova")
    return [v["name"] for v in _S["variables"] if v["role"] == "Y" or not only_y]


def _set_transform(method):
    s = _excluded_scores()
    _S["transform"] = {n: remedies.transform(s[n], method)[1] for n in _transform_names()} if method else None


def _checks(scores, transformed):
    out = []
    ranges = _S["info"]["score_range"]
    warns = [w for w in _S["info"]["warnings"] if w.get("row") not in _S["excluded"]]
    for t in tg.build_targets(scores, _S["variables"], _S["goal"]):
        c = normality.check_target(t, _S["goal"], _S["alpha"])
        y = t["y"] or t["label"]
        rng = None if transformed else ranges.get(y)
        yv = scores.loc[[r - 1 for r in t["rows"]], t["y"]].to_numpy() if t["kind"] == "residual" else t["values"]
        c["findings"] = dg.diagnose(t, c["moments"] or {}, rng, yv, warns) if c["moments"] else []
        for f in c["findings"]:
            f["table"] = _row_table(t, scores, f["rows"]) if f["rows"] else None
        out.append(c)
    return out


def _row_table(t, scores, rows):
    """Tabel baris terkait temuan: regresi -> Y, X, residual terstandar, Cook's D; lainnya -> nilai yang diuji."""
    pos = {r: i for i, r in enumerate(t["rows"])}
    mod, y = t.get("model"), t["y"]
    xs = [v["name"] for v in _S["variables"] if v["role"] == "X"]
    rd = lambda v: None if pd.isna(v) else round(float(v), 3)
    if mod:
        cols = ["Baris", y, *xs, "Residual terstandar", "Cook's D"]
        body = [[r, *(rd(scores.loc[r - 1][c]) for c in (y, *xs)), rd(mod["std_resid"][pos[r]]), rd(mod["cooks"][pos[r]])] for r in rows]
    elif t["kind"] == "residual":
        cols, body = ["Baris", y, "Residual"], [[r, rd(scores.loc[r - 1][y]), rd(t["values"][pos[r]])] for r in rows]
    else:
        cols, body = ["Baris", "Nilai"], [[r, rd(t["values"][pos[r]])] for r in rows]
    return {"columns": cols, "rows": body}


def _cell(v):
    """Nilai sel untuk dicatat: kosong -> "kosong", bilangan bulat -> int."""
    if v is None or (isinstance(v, str) and not v.strip()) or (not isinstance(v, str) and pd.isna(v)):
        return _BLANK
    if isinstance(v, np.generic):
        v = v.item()
    return int(v) if isinstance(v, float) and v.is_integer() else v


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
    if column not in raw.columns:
        raise ValueError(f"Kolom \"{column}\" tidak ditemukan.")
    if not 1 <= row <= len(raw):
        raise ValueError(f"Baris {row} tidak ada di data.")
    old, new = _cell(raw.at[row - 1, column]), _cell(value)
    prev = next((f for f in _S["fixes"] if f["row"] == row and f["column"] == column), None)
    if prev:
        old = prev["old"]
        _S["fixes"].remove(prev)
    raw[column] = raw[column].astype(object)
    raw.at[row - 1, column] = None if new == _BLANK else value
    if old != new:
        _S["fixes"].append({"row": row, "column": column, "old": old, "new": new})
    return {"ok": True}


@_endpoint
def prepare(variables, group=None):
    _need()
    group = group or None
    for c in [c for v in variables for c in v["columns"]] + ([group] if group else []):
        if c not in _S["raw"].columns:
            raise ValueError(f"Kolom \"{c}\" tidak ditemukan.")
    scores, info = prep.build_scores(_S["raw"], variables, group)
    for k in ("goal", "alpha", "checks"):
        _S.pop(k, None)
    _S.update(variables=variables, group=group, scores=scores, info=info, excluded={}, transform=None, alternatives=[])
    prev = scores.head(10)
    groups = scores["__group"].astype(str).value_counts().sort_index().to_dict() if "__group" in scores else None
    return {**info, "groups": groups, "preview": [{"row": int(i) + 1, **r} for i, r in zip(prev.index, prev.to_dict("records"))]}


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
        _set_transform(method)  # method null = batalkan transformasi
    elif kind == "exclude":
        ex = {int(r): k for r, k in reasons.items()}
        remedies.exclude_rows(_S["scores"], ex)  # validasi alasan/baris sebelum disimpan
        _S["excluded"] = ex
        _S["alternatives"] = []  # hasil alternatif lama dihitung dari data sebelum pengeluaran
        if _S["transform"]:
            _set_transform(next(iter(_S["transform"].values()))["method"])
    else:
        raise ValueError(f"Jenis perbaikan tidak dikenal: {kind}.")
    out = {"before": before, "after": _checks(_work(), _S["transform"] is not None)}
    return {"info": _S["transform"], **out} if kind == "transform" else out


@_endpoint
def report(chosen_id=None):
    _need("scores")
    _need("checks")
    alts = _S["alternatives"]["alternatives"] if _S["alternatives"] else []
    chosen = next((a for a in alts if a["id"] == chosen_id), None) if chosen_id else None
    tr = None if chosen else _S["transform"]  # alternatif dijalankan pada data tanpa transformasi
    after = _checks(_work(not chosen), not chosen and tr is not None) if (tr or _S["excluded"]) else []
    return rp.build_report({"goal": _S["goal"], "checks": _S["checks"], "fixes": _S["fixes"], "excluded": _S["excluded"],
                            "transform": tr, "chosen": chosen, "after": after})
