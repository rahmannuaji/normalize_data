import numpy as np, pandas as pd, pytest
from cekdata.target import build_targets, GoalError

V = [{"name": "Y1", "role": "Y"}, {"name": "X1", "role": "X"}, {"name": "X2", "role": "X"}]

def scores(groups):
    rng = np.random.default_rng(3); n = 60
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    return pd.DataFrame({"Y1": 1 + x1 + 0.5 * x2 + rng.normal(size=n), "X1": x1, "X2": x2,
                         "__group": np.resize(groups, n)}, index=range(10, 10 + n))

def test_regression_residuals():
    [t] = build_targets(scores(["L", "P"]), V, "regression")
    assert t["kind"] == "residual" and t["label"] == "Residual regresi: X1, X2 → Y1"
    assert abs(t["values"].mean()) < 1e-9 and t["rows"][0] == 11
    assert t["model"]["mahal_p"] is not None

def test_ttest_ind_two_groups():
    ts = build_targets(scores(["L", "P"]), V, "ttest_ind")
    assert [t["label"] for t in ts] == ["Y1 (kelompok L)", "Y1 (kelompok P)"] and ts[0]["groups_n"] == [30, 30]

def test_ttest_ind_rejects_three_groups():
    with pytest.raises(GoalError, match="tepat 2 kelompok"):
        build_targets(scores(["A", "B", "C"]), V, "ttest_ind")

def test_anova_rejects_two_groups():
    with pytest.raises(GoalError, match="minimal 3 kelompok"):
        build_targets(scores(["L", "P"]), V, "anova")

def test_paired_needs_two_y():
    with pytest.raises(GoalError, match="dua variabel Y"):
        build_targets(scores(["L", "P"]), V, "ttest_paired")

def test_anova_residual_and_paired_and_variable():
    s = scores(["A", "B", "C"])
    [t] = build_targets(s, V, "anova")
    assert t["label"] == "Residual ANOVA: Y1 ~ kelompok" and t["groups_n"] == [20, 20, 20] and t["kind"] == "residual"
    v2 = [{"name": "Y1", "role": "Y"}, {"name": "X1", "role": "Y"}]
    [d] = build_targets(s, v2, "ttest_paired")
    assert d["label"] == "Selisih X1 − Y1" and np.allclose(d["values"], s["X1"] - s["Y1"])
    assert [t["label"] for t in build_targets(s, V, "normality_only")] == ["Y1", "X1", "X2"]
    with pytest.raises(GoalError, match="kolom kelompok"):
        build_targets(s.drop(columns="__group"), V, "anova")

def test_correlation_needs_y_and_x():
    with pytest.raises(GoalError, match="Korelasi butuh minimal satu Y dan satu X"):
        build_targets(scores(["L", "P"]), [{"name": "Y1", "role": "Y"}, {"name": "X1", "role": "Y"}], "correlation")
