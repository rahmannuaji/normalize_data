import numpy as np
import statsmodels.api as sm
from scipy import stats

GOALS = ("correlation", "regression", "ttest_ind", "ttest_paired", "anova", "normality_only")


class GoalError(ValueError):
    pass


def _t(label, kind, values, idx, groups_n=None, y=None, model=None):
    return {"label": label, "kind": kind, "values": np.asarray(values, dtype=float),
            "rows": [int(i) + 1 for i in idx], "groups_n": groups_n, "y": y, "model": model}


def _regression(scores, y, xs):
    X = sm.add_constant(scores[xs].astype(float))
    fit = sm.OLS(scores[y].astype(float), X).fit()
    infl = fit.get_influence()
    mahal_p = None
    if len(xs) >= 2:
        d = scores[xs].to_numpy(float) - scores[xs].to_numpy(float).mean(axis=0)
        d2 = np.einsum("ij,jk,ik->i", d, np.linalg.pinv(np.cov(d, rowvar=False)), d)
        mahal_p = stats.chi2.sf(d2, len(xs))
    model = {"std_resid": np.asarray(infl.resid_studentized_internal), "cooks": np.asarray(infl.cooks_distance[0]),
             "mahal_p": mahal_p, "fitted": np.asarray(fit.fittedvalues)}
    return _t(f"Residual regresi: {', '.join(xs)} → {y}", "residual", fit.resid, scores.index, y=y, model=model)


def build_targets(scores, variables, goal):
    ys = [v["name"] for v in variables if v["role"] == "Y"]
    xs = [v["name"] for v in variables if v["role"] == "X"]
    if goal in ("correlation", "normality_only"):
        return [_t(c, "variable", scores[c], scores.index) for c in (v["name"] for v in variables)]
    if goal == "regression":
        if not xs:
            raise GoalError("Regresi butuh minimal satu variabel X.")
        return [_regression(scores, y, xs) for y in ys]
    if goal == "ttest_paired":
        if len(ys) < 2:
            raise GoalError("Uji-t berpasangan butuh dua variabel Y (Y1 = sebelum, Y2 = sesudah).")
        return [_t(f"Selisih {ys[1]} − {ys[0]}", "difference", scores[ys[1]] - scores[ys[0]], scores.index)]
    if goal not in ("ttest_ind", "anova"):
        raise GoalError(f"Tujuan analisis tidak dikenal: {goal}.")
    if "__group" not in scores:
        raise GoalError("Tujuan ini butuh kolom kelompok.")
    g = scores["__group"]
    levels = sorted(g.unique(), key=str)
    k = len(levels)
    if goal == "ttest_ind":
        if k != 2:
            raise GoalError(f"Uji-t independen butuh kolom kelompok dengan tepat 2 kelompok (sekarang {k}).")
        n = [int((g == lv).sum()) for lv in levels]
        return [_t(f"{y} (kelompok {lv})", "group", scores.loc[g == lv, y], scores.index[g == lv], n, y)
                for y in ys for lv in levels]
    if k < 3:
        raise GoalError(f"ANOVA butuh kolom kelompok dengan minimal 3 kelompok (sekarang {k}).")
    n = [int((g == lv).sum()) for lv in levels]
    return [_t(f"Residual ANOVA: {y} ~ kelompok", "residual", scores[y] - scores.groupby(g)[y].transform("mean"),
               scores.index, n, y) for y in ys]
