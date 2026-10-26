import numpy as np
from scipy import stats
from statsmodels.stats.diagnostic import lilliefors, normal_ad

NAMES = {
    "shapiro": "Shapiro-Wilk",
    "lilliefors": "Kolmogorov-Smirnov (Lilliefors)",
    "ks_classic": "Kolmogorov-Smirnov klasik (SPSS)",
    "anderson": "Anderson-Darling",
    "jarque_bera": "Jarque-Bera",
    "dagostino": "D'Agostino-Pearson K²",
    "skew_kurt": "Skewness & kurtosis (z)",
}
MIN_N = {"shapiro": 3, "lilliefors": 4, "ks_classic": 4, "anderson": 8,
         "jarque_bera": 8, "dagostino": 8, "skew_kurt": 4}
T_GROUP_GOALS = {"ttest_ind", "ttest_paired", "anova"}


def _fmt(v):
    return f"{v:.2f}".replace("-", "−").replace(".", ",")


def _fmt_p(p):
    return "< 0,001" if p < 0.001 else "= " + f"{p:.3f}".replace(".", ",")


def moments(x):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 4:
        return dict.fromkeys(["skew", "kurt", "se_skew", "se_kurt", "z_skew", "z_kurt"])
    skew = float(stats.skew(x, bias=False))
    kurt = float(stats.kurtosis(x, bias=False))
    se_s = float(np.sqrt(6 * n * (n - 1) / ((n - 2) * (n + 1) * (n + 3))))
    se_k = float(2 * se_s * np.sqrt((n * n - 1) / ((n - 3) * (n + 5))))
    return {"skew": skew, "kurt": kurt, "se_skew": se_s, "se_kurt": se_k,
            "z_skew": skew / se_s, "z_kurt": kurt / se_k}


def run_tests(x, alpha=0.05):
    x = np.asarray(x, dtype=float)
    n = len(x)
    m = moments(x) if n >= 4 else None
    calls = {
        "shapiro": lambda: stats.shapiro(x),
        # "approx" (Dallal-Wilkinson untuk p < 0,1, seperti nortest::lillie.test di R): "table" memotong p kecil
        # tepat di 0,001 sehingga akan terbaca "p = 0,001" padahal sebenarnya p < 0,001.
        "lilliefors": lambda: lilliefors(x, dist="norm", pvalmethod="approx"),
        "ks_classic": lambda: stats.kstest(x, stats.norm(x.mean(), x.std(ddof=1)).cdf),
        "anderson": lambda: normal_ad(x),
        "jarque_bera": lambda: stats.jarque_bera(x),
        "dagostino": lambda: stats.normaltest(x),
    }
    out = []
    for tid, name in NAMES.items():
        t = {"id": tid, "name": name, "stat": None, "p": None, "rejected": None, "skipped_reason": None}
        if n < MIN_N[tid]:
            t["skipped_reason"] = f"Butuh minimal {MIN_N[tid]} data"
        elif tid == "skew_kurt":
            t["stat"] = f"{m['skew']:.2f}; {m['kurt']:.2f}"
            if n > 300:
                t["rejected"] = bool(abs(m["skew"]) >= 2 or abs(m["kurt"]) >= 7)
            else:
                lim = 1.96 if n < 50 else 3.29
                t["rejected"] = bool(max(abs(m["z_skew"]), abs(m["z_kurt"])) >= lim)
        else:
            s, p = calls[tid]()[:2]
            t["stat"], t["p"] = float(s), float(p)
            t["rejected"] = bool(p < alpha)
        out.append(t)
    return out


def decide_status(n, sw_p, skew, kurt, z_skew, z_kurt, goal, groups_n, alpha):
    if n < 50:
        status, rule = ("bad" if sw_p < alpha else "ok"), "n<50"
    elif n <= 300:
        if sw_p >= alpha:
            status = "ok"
        else:
            status = "warn" if max(abs(z_skew), abs(z_kurt)) < 3.29 else "bad"
        rule = "50-300"
    else:
        if abs(skew) >= 2 or abs(kurt) >= 7:
            status = "bad"
        else:
            status = "warn" if sw_p < alpha else "ok"
        rule = ">300"
    if (status == "bad" and goal in T_GROUP_GOALS and groups_n and min(groups_n) >= 30
            and abs(skew) < 2 and abs(kurt) < 7):
        status = "warn"
    return status, rule


def _reason(rule, sw_p, m):
    p = _fmt_p(sw_p)
    if rule == "n<50":
        return f"Untuk n kurang dari 50 dipakai Shapiro-Wilk (p {p}; Ghasemi & Zahediasl, 2012)."
    if rule == "50-300":
        return (f"Untuk n antara 50 dan 300 dipakai Shapiro-Wilk (p {p}) ditambah "
                f"z-skewness/kurtosis (batas 3,29; Kim, 2013).")
    return (f"Untuk n di atas 300 dipakai skewness {_fmt(m['skew'])} (batas 2) dan kurtosis "
            f"{_fmt(m['kurt'])} (batas 7) ditambah Shapiro-Wilk (p {p}; Kim, 2013).")


def check_target(target, goal, alpha=0.05):
    x = np.asarray(target["values"], dtype=float)
    n = len(x)
    res = {"label": target["label"], "n": n, "tests": [], "moments": None,
           "verdict": {"status": "skipped", "rule": None, "reason": "", "rejected": 0, "total": 0},
           "plot": {"values": x.tolist(), "qq": {"theoretical": [], "sample": [], "rows": []},
                    "pp": {"expected": [], "observed": []}},
           "notes": []}
    if n < 3:
        res["verdict"]["reason"] = "Data kurang dari 3."
        return res
    if np.std(x) == 0:
        res["verdict"]["reason"] = "Semua nilai sama, normalitas tidak bisa diuji."
        return res

    tests = run_tests(x, alpha)
    m = moments(x)
    run = [t for t in tests if t["skipped_reason"] is None]
    sw_p = tests[0]["p"]
    # n == 3 has no moments; Shapiro alone decides
    mm = m if m["skew"] is not None else {"skew": 0.0, "kurt": 0.0, "z_skew": 0.0, "z_kurt": 0.0}
    status, rule = decide_status(n, sw_p, mm["skew"], mm["kurt"], mm["z_skew"], mm["z_kurt"],
                                 goal, target.get("groups_n"), alpha)
    res["tests"], res["moments"] = tests, m
    base = decide_status(n, sw_p, mm["skew"], mm["kurt"], mm["z_skew"], mm["z_kurt"], goal, None, alpha)[0]
    res["verdict"] = {"status": status, "rule": rule, "reason": _reason(rule, sw_p, mm),
                      "rejected": sum(t["rejected"] for t in run), "total": len(run),
                      "override": "kelompok_besar" if base != status else None}

    order = np.argsort(x, kind="stable")
    z = (x[order] - x.mean()) / x.std(ddof=1)
    i = np.arange(1, n + 1)
    rows = list(target["rows"])
    res["plot"]["qq"] = {"theoretical": stats.norm.ppf((i - 0.375) / (n + 0.25)).tolist(),
                         "sample": z.tolist(), "rows": [rows[j] for j in order]}
    res["plot"]["pp"] = {"expected": ((i - 0.5) / n).tolist(), "observed": stats.norm.cdf(z).tolist()}
    if n > 5000:
        res["notes"].append("p-value Shapiro-Wilk kurang akurat untuk n > 5000")
    if n < 20:
        res["notes"].append("Uji D'Agostino-Pearson kurang akurat untuk n < 20.")
    return res
