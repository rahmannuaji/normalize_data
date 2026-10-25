import numpy as np, pandas as pd, pytest
from cekdata.remedies import alternative, bootstrap_ols, dunn, transform, exclude_rows

def test_bootstrap_recovers_slope_and_is_deterministic():
    rng = np.random.default_rng(5); x = rng.normal(size=200); y = 2 + 0.5 * x + rng.normal(scale=.3, size=200)
    a = bootstrap_ols(y, x[:, None], ["X1"]); b = bootstrap_ols(y, x[:, None], ["X1"])
    assert a == b and a["names"] == ["Konstanta", "X1"]
    assert a["ci_low"][1] < 0.5 < a["ci_high"][1]

def test_dunn_bonferroni():
    v = np.r_[np.arange(10), np.arange(10) + 20, np.arange(10) + 40.0]; g = np.repeat(["A", "B", "C"], 10)
    res = dunn(v, g)
    assert len(res) == 3 and all(r["p_adj"] == pytest.approx(min(1, r["p"] * 3)) for r in res)
    assert next(r for r in res if {r["a"], r["b"]} == {"A", "C"})["p_adj"] < 0.05

def test_boxcox_shifts_nonpositive():
    t, info = transform(np.array([0.0, 1, 2, 3, 10]), "boxcox")
    assert info["shift"] == 1 and np.isfinite(t).all() and info["lambda"] is not None

def test_left_skew_is_reflected_for_log():
    _, info = transform(np.array([1.0, 8, 9, 9, 10, 10, 10]), "log")
    assert info["reflected"] is True

def test_exclude_requires_valid_reason():
    s = pd.DataFrame({"Y1": [1.0, 2, 3]})
    assert exclude_rows(s, {2: "salah_input"}).index.tolist() == [0, 2]
    with pytest.raises(ValueError, match="alasan"):
        exclude_rows(s, {2: ""})

def test_alternative_regression_has_bootstrap_and_hc3():
    rng = np.random.default_rng(1); x = rng.normal(size=80)
    s = pd.DataFrame({"Y1": x + rng.exponential(size=80), "X1": x})
    out = alternative(s, [{"name": "Y1", "role": "Y"}, {"name": "X1", "role": "X"}], "regression")
    assert [a["id"] for a in out["alternatives"]][:2] == ["bootstrap", "hc3"]

def _vars(*ys, xs=()):
    return [{"name": n, "role": "Y"} for n in ys] + [{"name": n, "role": "X"} for n in xs]

def test_alternative_other_goals_and_json_types():
    import json
    rng = np.random.default_rng(2); n = 60
    s = pd.DataFrame({"Y1": rng.exponential(size=n), "Y2": rng.exponential(size=n), "X1": rng.normal(size=n),
                      "__group": np.tile(["A", "B", "C"], 20)})
    c = alternative(s, _vars("Y1", xs=["X1"]), "correlation")
    assert [a["id"] for a in c["alternatives"]] == ["spearman", "kendall"] and c["posthoc"] is None
    assert c["alternatives"][1]["recommended"] is False
    p = alternative(s, _vars("Y1", "Y2"), "ttest_paired")
    assert p["alternatives"][0]["id"] == "wilcoxon"
    a = alternative(s, _vars("Y1"), "anova")
    assert a["alternatives"][0]["id"] == "kruskal" and len(a["posthoc"]) == 3
    t = alternative(s[s.__group != "C"], _vars("Y1"), "ttest_ind")
    assert t["alternatives"][0]["id"] == "mannwhitney" and -1 <= t["alternatives"][0]["effect"] <= 1
    assert alternative(s, _vars("Y1"), "normality_only") == {"parametric": [], "alternatives": [], "posthoc": None}
    for o in (c, p, a, t, alternative(s, _vars("Y1", xs=["X1"]), "regression")):
        json.dumps(o)
