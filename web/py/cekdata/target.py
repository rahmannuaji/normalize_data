import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

from . import UserError

GOALS = ("correlation", "regression", "ttest_ind", "ttest_paired", "anova", "normality_only")


class GoalError(UserError):
    pass


def _and(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " dan " + names[-1]


def _t(label, subject, kind, values, idx, groups_n=None, y=None, model=None, y_values=None):
    """label: judul singkat di UI; subject: frasa untuk kalimat laporan ("Uji normalitas dilakukan terhadap …")."""
    return {"label": label, "subject": subject, "kind": kind, "values": np.asarray(values, dtype=float),
            "rows": [int(i) + 1 for i in idx], "groups_n": groups_n, "y": y, "model": model,
            "y_values": None if y_values is None else np.asarray(y_values, dtype=float)}


def _regression(scores, y, xs):
    X = scores[xs].astype(float)
    fit = sm.OLS(scores[y].astype(float), sm.add_constant(X)).fit()
    infl = fit.get_influence()
    mahal_p = None
    if len(xs) >= 2:
        d = X.to_numpy() - X.to_numpy().mean(axis=0)
        d2 = np.einsum("ij,jk,ik->i", d, np.linalg.pinv(np.cov(d, rowvar=False)), d)
        mahal_p = stats.chi2.sf(d2, len(xs))
    model = {"std_resid": np.asarray(infl.resid_studentized_internal), "cooks": np.asarray(infl.cooks_distance[0]),
             "mahal_p": mahal_p, "fitted": np.asarray(fit.fittedvalues)}
    return _t(f"Residual regresi: {', '.join(xs)} → {y}", f"residual model regresi {_and(xs)} terhadap {y}", "residual", fit.resid, scores.index, y=y, model=model, y_values=scores[y])


def _anova_resid(scores, y):
    d = pd.DataFrame({"y": scores[y].astype(float), "g": scores["__group"].astype(str)})
    return smf.ols("y ~ C(g)", d).fit().resid


def build_targets(scores, variables, goal):
    ys = [v["name"] for v in variables if v["role"] == "Y"]
    xs = [v["name"] for v in variables if v["role"] == "X"]
    if goal == "correlation" and not (ys and xs):
        raise GoalError("Korelasi butuh minimal satu Y dan satu X.")
    if goal in ("correlation", "normality_only"):
        return [_t(c, f"variabel {c}", "variable", scores[c], scores.index) for c in (v["name"] for v in variables)]
    if goal == "regression":
        if not xs:
            raise GoalError("Regresi butuh minimal satu variabel X.")
        return [_regression(scores, y, xs) for y in ys]
    if goal == "ttest_paired":
        if len(ys) < 2:
            raise GoalError("Uji-t berpasangan butuh dua variabel Y (Y1 = sebelum, Y2 = sesudah).")
        return [_t(f"Selisih {ys[1]} − {ys[0]}", f"selisih {ys[1]} − {ys[0]}", "difference", scores[ys[1]] - scores[ys[0]], scores.index)]
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
        return [_t(f"{y} (kelompok {lv})", f"{y} pada kelompok {lv}", "group", scores.loc[g == lv, y], scores.index[g == lv], n, y)
                for y in ys for lv in levels]
    if k < 3:
        raise GoalError(f"ANOVA butuh kolom kelompok dengan minimal 3 kelompok (sekarang {k}).")
    n = [int((g == lv).sum()) for lv in levels]
    return [_t(f"Residual ANOVA: {y} ~ kelompok", f"residual model ANOVA satu arah {y} berdasarkan kelompok", "residual", _anova_resid(scores, y),
               scores.index, n, y, y_values=scores[y]) for y in ys]
