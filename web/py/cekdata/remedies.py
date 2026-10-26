import numpy as np
import statsmodels.api as sm
from scipy import stats

from . import UserError

REASONS = {"salah_input": "Salah input", "menjawab_asal": "Responden menjawab asal",
           "di_luar_populasi": "Di luar populasi penelitian"}


def _res(id_, name, label, stat_name, stat, p, df=None, ci=None, effect=None, effect_name=None, **extra):
    """stat_name: simbol statistik untuk laporan (t, F, U, W, H, r, ρ, τ, B); df: angka, [df1, df2], atau None."""
    f = lambda v: None if v is None else float(v)
    return {"id": id_, "name": name, "label": label, "stat_name": stat_name, "stat": f(stat), "p": f(p),
            "df": [f(v) for v in df] if isinstance(df, (list, tuple)) else f(df),
            "ci": None if ci is None else [float(ci[0]), float(ci[1])], "effect": f(effect),
            "effect_name": None if effect is None else effect_name, **extra}


def bootstrap_ols(y, X, names, n_boot=5000, seed=2026):
    y = np.asarray(y, float)
    A = np.column_stack([np.ones(len(y)), np.asarray(X, float)])
    n = len(y)
    rng = np.random.default_rng(seed)
    k = A.shape[1]
    P = (A[:, :, None] * A[:, None, :]).reshape(n, k * k)
    Q = A * y[:, None]
    coefs = np.empty((n_boot, k))
    for s in range(0, n_boot, 250):
        c = min(250, n_boot - s)
        idx = rng.integers(0, n, (c, n))  # same stream as c sequential draws of n
        W = np.bincount((idx + np.arange(c)[:, None] * n).ravel().astype(np.intp), minlength=c * n).reshape(c, n)
        try:
            coefs[s:s + c] = np.linalg.solve((W @ P).reshape(c, k, k), (W @ Q)[:, :, None])[:, :, 0]
        except np.linalg.LinAlgError:  # resample with collinear columns: fall back to lstsq
            for b in range(c):
                i = idx[b]
                coefs[s + b] = np.linalg.lstsq(A[i], y[i], rcond=None)[0]
    return {"names": ["Konstanta", *names], "coef": np.linalg.lstsq(A, y, rcond=None)[0].tolist(),
            "ci_low": np.percentile(coefs, 2.5, axis=0).tolist(),
            "ci_high": np.percentile(coefs, 97.5, axis=0).tolist()}


def dunn(values, groups):
    v = np.asarray(values, float)
    g = np.asarray(groups).astype(str)
    N = len(v)
    ranks = stats.rankdata(v)
    _, counts = np.unique(v, return_counts=True)
    var0 = N * (N + 1) / 12 - (counts ** 3 - counts).sum() / (12 * (N - 1))
    levels = sorted(set(g))
    m = len(levels) * (len(levels) - 1) // 2
    out = []
    for i, a in enumerate(levels):
        for b in levels[i + 1:]:
            ra, rb = ranks[g == a], ranks[g == b]
            z = (ra.mean() - rb.mean()) / np.sqrt(var0 * (1 / len(ra) + 1 / len(rb)))
            p = 2 * stats.norm.sf(abs(z))
            out.append({"a": a, "b": b, "z": float(z), "p": float(p), "p_adj": float(min(1.0, p * m))})
    return out


def transform(x, method):
    x = np.asarray(x, float)
    if np.ptp(x) == 0:
        raise UserError("Semua nilai sama, jadi data tidak bisa ditransformasi.")
    shift, reflected, lam = 0.0, False, None
    if method == "yeojohnson":
        t, lam = stats.yeojohnson(x)
    elif method in ("log", "sqrt", "reciprocal", "boxcox"):
        if stats.skew(x) < 0:
            x = x.max() + 1 - x
            reflected = True
        lo = x.min()
        if (method == "sqrt" and lo < 0) or (method != "sqrt" and lo <= 0):
            shift = 1 - lo
            x = x + shift
        if method == "log":
            t = np.log(x)
        elif method == "sqrt":
            t = np.sqrt(x)
        elif method == "reciprocal":
            t = 1 / x
        else:
            t, lam = stats.boxcox(x)
    else:
        raise UserError(f"Metode transformasi tidak dikenal: {method}.")
    return np.asarray(t).tolist(), {"method": method, "lambda": None if lam is None else float(lam),
                                    "shift": float(shift), "reflected": reflected}


def exclude_rows(scores, reasons):
    for row, r in reasons.items():
        if r not in REASONS:
            raise UserError("Setiap baris yang dikeluarkan wajib punya alasan.")
        if row - 1 not in scores.index:
            raise UserError(f"Baris {row} tidak ada.")
    return scores.drop(index=[r - 1 for r in reasons])


def _fisher_ci(r, n, se):
    if n <= 3 or abs(r) >= 1:
        return None
    z, h = np.arctanh(r), 1.959964 * se
    return np.tanh(z - h), np.tanh(z + h)


def _corr(scores, ys, xs):
    par, sp, ke = [], [], []
    for y in ys:
        for x in xs:
            d = scores[[y, x]].dropna().astype(float)
            a, b, n = d[y].to_numpy(), d[x].to_numpy(), len(d)
            lab = f"{x} dan {y}"
            r, p = stats.pearsonr(a, b)
            par.append(_res("pearson", "Pearson", lab, "r", r, p, ci=_fisher_ci(r, n, 1 / np.sqrt(max(n - 3, 1))), effect=r, effect_name="r"))
            rho, p = stats.spearmanr(a, b)
            sp.append(_res("spearman", "Spearman", lab, "ρ", rho, p,
                           ci=_fisher_ci(rho, n, np.sqrt((1 + rho ** 2 / 2) / max(n - 3, 1))), effect=rho, effect_name="ρ"))
            tau, p = stats.kendalltau(a, b)
            uniq = min(len(np.unique(a)), len(np.unique(b))) / n
            ke.append(_res("kendall", "Kendall tau-b", lab, "τ", tau, p, effect=tau, effect_name="τ", recommended=bool(uniq < 0.5)))
    return par, sp + ke, None


def _regr(scores, ys, xs):
    par, boot, hc = [], [], []
    for y in ys:
        d = scores[[y, *xs]].dropna().astype(float)
        A = sm.add_constant(d[xs])
        model = sm.OLS(d[y], A)
        fit = model.fit()
        rob = model.fit(cov_type="HC3", use_t=True)
        bs = bootstrap_ols(d[y].to_numpy(), d[xs].to_numpy(), xs)
        for j, x in enumerate(xs):
            lab = f"{x} terhadap {y}"
            beta = fit.params[x] * d[x].std() / d[y].std()
            par.append(_res("ols", "Regresi OLS", lab, "B", fit.params[x], fit.pvalues[x], fit.df_resid,
                            fit.conf_int().loc[x], beta, "β terstandar", t=float(fit.tvalues[x])))
            boot.append(_res("bootstrap", "Bootstrap (5.000 sampel)", lab, "B", bs["coef"][j + 1], None, None,
                             (bs["ci_low"][j + 1], bs["ci_high"][j + 1]), beta, "β terstandar"))
            hc.append(_res("hc3", "Galat baku robust (HC3)", lab, "B", rob.params[x], rob.pvalues[x], rob.df_resid,
                           rob.conf_int().loc[x], beta, "β terstandar", t=float(rob.tvalues[x])))
    return par, boot + hc, None


def _groups(scores, y):
    d = scores[[y, "__group"]].dropna()
    lv = sorted(d["__group"].unique(), key=str)
    return lv, [d.loc[d["__group"] == l, y].astype(float).to_numpy() for l in lv]


def _ind(scores, ys, xs):
    par, alt = [], []
    for y in ys:
        lv, (a, b) = _groups(scores, y)
        lab = f"{y} antara {lv[0]} dan {lv[1]}"
        t = stats.ttest_ind(a, b, equal_var=False)
        ci = t.confidence_interval()
        sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
        par.append(_res("welch", "Uji-t Welch", lab, "t", t.statistic, t.pvalue, t.df, (ci.low, ci.high),
                        (a.mean() - b.mean()) / sp, "d (Cohen)"))
        u = stats.mannwhitneyu(a, b, alternative="two-sided")
        alt.append(_res("mannwhitney", "Mann-Whitney U", lab, "U", u.statistic, u.pvalue, None, None,
                        2 * u.statistic / (len(a) * len(b)) - 1, "r rank-biserial"))
    return par, alt, None


def _paired(scores, ys, xs):
    d = scores[[ys[0], ys[1]]].dropna().astype(float)
    diff = (d[ys[1]] - d[ys[0]]).to_numpy()
    lab = f"{ys[1]} − {ys[0]}"
    t = stats.ttest_1samp(diff, 0.0)
    ci = t.confidence_interval()
    par = [_res("paired", "Uji-t berpasangan", lab, "t", t.statistic, t.pvalue, t.df, (ci.low, ci.high),
                diff.mean() / diff.std(ddof=1), "d_z")]
    nz = diff[diff != 0]
    rk = stats.rankdata(np.abs(nz))
    rbc = (rk[nz > 0].sum() - rk[nz < 0].sum()) / rk.sum() if len(nz) else 0.0
    w = stats.wilcoxon(diff)
    return par, [_res("wilcoxon", "Wilcoxon signed-rank", lab, "W", w.statistic, w.pvalue, None, None, rbc, "r rank-biserial")], None


def _anova(scores, ys, xs):
    par, alt, post = [], [], []
    for y in ys:
        lv, gs = _groups(scores, y)
        lab = f"{y} antar kelompok"
        allv = np.concatenate(gs)
        n, k = len(allv), len(gs)
        f = stats.f_oneway(*gs)
        ssb = sum(len(g) * (g.mean() - allv.mean()) ** 2 for g in gs)
        par.append(_res("anova", "ANOVA satu arah", lab, "F", f.statistic, f.pvalue, [k - 1, n - k], None,
                        ssb / ((allv - allv.mean()) ** 2).sum(), "η²"))
        h = stats.kruskal(*gs)
        alt.append(_res("kruskal", "Kruskal-Wallis", lab, "H", h.statistic, h.pvalue, k - 1, None, h.statistic / (n - 1), "ε²"))
        d = scores[[y, "__group"]].dropna()
        post += [{**r, "y": y, "label": f"{y} antara {r['a']} dan {r['b']}"}
                 for r in dunn(d[y].to_numpy(), d["__group"].to_numpy())]
    return par, alt, post


_RUN = {"correlation": _corr, "regression": _regr, "ttest_ind": _ind, "ttest_paired": _paired, "anova": _anova}


def alternative(scores, variables, goal):
    if goal == "normality_only":
        return {"parametric": [], "alternatives": [], "posthoc": None}
    ys = [v["name"] for v in variables if v["role"] == "Y"]
    xs = [v["name"] for v in variables if v["role"] == "X"]
    if goal == "ttest_paired":
        if np.ptp((scores[ys[1]] - scores[ys[0]]).astype(float)) == 0:
            raise UserError(f"Selisih {ys[1]} − {ys[0]} sama untuk semua responden, jadi analisis alternatif tidak bisa dijalankan.")
    else:
        for y in ys:
            if np.ptp(scores[y].astype(float)) == 0:
                raise UserError(f"Semua nilai {y} sama, jadi analisis alternatif tidak bisa dijalankan.")
    par, alt, post = _RUN[goal](scores, ys, xs)
    return {"parametric": par, "alternatives": alt, "posthoc": post}
