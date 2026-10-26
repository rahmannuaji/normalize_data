import numpy as np, pytest
from scipy.stats import norm, expon
from cekdata.normality import moments, run_tests, decide_status, check_target

Q40 = (np.arange(1, 41) - 0.5) / 40

def test_shapiro_matches_r_reference():
    # R: shapiro.test(58:72) -> W = 0.96359, p-value = 0.7545
    t = run_tests(np.arange(58, 73, dtype=float))[0]
    assert t["id"] == "shapiro"
    assert t["stat"] == pytest.approx(0.96359, abs=1e-4) and t["p"] == pytest.approx(0.7545, abs=1e-3)

def test_se_formulas_n147():
    m = moments(norm.ppf((np.arange(1, 148) - 0.5) / 147))
    assert m["se_skew"] == pytest.approx(0.2000, abs=1e-3)
    assert m["se_kurt"] == pytest.approx(0.3975, abs=1e-3)

def test_all_seven_tests_present():
    assert [t["id"] for t in run_tests(norm.ppf(Q40))] == [
        "shapiro", "lilliefors", "ks_classic", "anderson", "jarque_bera", "dagostino", "skew_kurt"]

def test_small_n_skips_some_tests():
    tests = {t["id"]: t for t in run_tests(np.array([1.0, 2.0, 2.5, 4.0, 7.0]))}
    assert tests["shapiro"]["p"] is not None
    assert tests["dagostino"]["skipped_reason"] is not None

@pytest.mark.parametrize("args,expected", [
    ((30, 0.01, 0.5, 0.1, 1.2, 0.1, "regression", None), ("bad", "n<50")),
    ((30, 0.20, 0.5, 0.1, 1.2, 0.1, "regression", None), ("ok", "n<50")),
    ((147, 0.001, -1.12, 0.84, -5.6, 2.1, "regression", None), ("bad", "50-300")),
    ((147, 0.02, -0.4, 0.3, -2.0, 0.8, "regression", None), ("warn", "50-300")),
    ((500, 0.0001, 0.6, 1.0, 5.5, 4.6, "regression", None), ("warn", ">300")),
    ((500, 0.0001, 2.3, 1.0, 21.0, 4.6, "regression", None), ("bad", ">300")),
    ((500, 0.30, 0.1, 0.1, 0.9, 0.5, "regression", None), ("ok", ">300")),
    ((147, 0.001, -1.12, 0.84, -5.6, 2.1, "ttest_ind", [70, 77]), ("warn", "50-300")),
    ((60, 0.001, -1.12, 0.84, -3.6, 2.1, "ttest_ind", [25, 35]), ("bad", "50-300")),
])
def test_decide_status(args, expected):
    assert decide_status(*args, alpha=0.05) == expected

def test_constant_values_skipped():
    r = check_target({"label": "Y1", "values": np.full(30, 5.0), "rows": list(range(1, 31)), "groups_n": None}, "normality_only")
    assert r["verdict"]["status"] == "skipped"

def test_check_target_exponential_bad_with_plot_data():
    x = expon.ppf(Q40)
    r = check_target({"label": "Y1", "values": x, "rows": list(range(1, 41)), "groups_n": None}, "normality_only")
    assert r["verdict"]["status"] == "bad"
    assert len(r["plot"]["qq"]["sample"]) == 40 and sorted(r["plot"]["qq"]["rows"]) == list(range(1, 41))

@pytest.mark.filterwarnings("ignore:scipy.stats.shapiro")
def test_note_for_n_above_5000():
    x = norm.ppf((np.arange(1, 5002) - 0.5) / 5001)
    r = check_target({"label": "Y1", "values": x, "rows": list(range(1, 5002)), "groups_n": None}, "normality_only")
    assert "p-value Shapiro-Wilk kurang akurat untuk n > 5000" in r["notes"]


def test_lilliefors_small_p_is_not_clipped_at_0001():
    # pvalmethod="table" memotong semua p kecil di batas tabel 0,001
    t = next(t for t in run_tests(expon.ppf((np.arange(1, 201) - 0.5) / 200)) if t["id"] == "lilliefors")
    assert 0 < t["p"] < 1e-6  # "table" memberi 0,000999… (batas tabel), bukan p sebenarnya


def test_reason_uses_unicode_minus():
    from cekdata.normality import _reason
    assert "skewness −1,20" in _reason(">300", 0.2, {"skew": -1.2, "kurt": 0.5})
