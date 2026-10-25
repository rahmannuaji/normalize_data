import numpy as np
from scipy.stats import norm
from cekdata.diagnose import diagnose
from cekdata.normality import moments

def tgt(x): return {"label": "Y1", "kind": "variable", "values": x, "rows": list(range(1, len(x) + 1)), "groups_n": None, "model": None}
ids = lambda f: [d["id"] for d in f]

def test_ceiling_found_with_rows():
    x = np.r_[np.full(30, 48.0), np.linspace(20, 44, 70)]
    f = diagnose(tgt(x), moments(x), [10, 50], x, [])
    c = next(d for d in f if d["id"] == "ceiling")
    assert c["severity"] == "high" and c["rows"] == list(range(1, 31))

def test_outlier_rows():
    x = np.r_[norm.ppf((np.arange(1, 100) - 0.5) / 99), 6.0]
    f = diagnose(tgt(x), moments(x), None, x, [])
    assert 100 in next(d for d in f if d["id"] == "outliers")["rows"]

def test_bimodal():
    x = np.r_[norm.ppf((np.arange(1, 51) - .5) / 50) - 3, norm.ppf((np.arange(1, 51) - .5) / 50) + 3]
    assert "bimodal" in ids(diagnose(tgt(x), moments(x), None, x, []))

def test_normal_has_no_findings():
    x = norm.ppf((np.arange(1, 101) - .5) / 100)
    assert diagnose(tgt(x), moments(x), None, x, []) == []

def test_prep_warnings_become_high_findings_first():
    x = norm.ppf((np.arange(1, 101) - .5) / 100)
    w = [{"kind": "out_of_range", "row": 87, "column": "S4", "value": 55.0}]
    f = diagnose(tgt(x), moments(x), None, x, w)
    assert f[0]["id"] == "data_error" and f[0]["rows"] == [87]

def test_tiny_n_and_extras():
    x = np.array([1.0, 2.0, 3.0])
    assert "low_variety" in ids(diagnose(tgt(x), moments(x), None, x, []))
    x = np.r_[np.zeros(80), np.full(20, 5.0)] + np.arange(100) * 1e-3
    f = diagnose(tgt(x), moments(x), None, x, [{"kind": "negative_item_total", "variable": "V", "item": "S2", "r": -0.4}])
    assert f[0]["id"] == "unreversed_item" and "-0,4" in f[0]["detail"]
    assert [d["severity"] for d in f] == sorted((d["severity"] for d in f), key=["high", "medium", "low"].index)
