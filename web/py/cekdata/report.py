"""Laporan Bab IV berbahasa Indonesia formal + daftar rujukan APA 7."""
from .remedies import REASONS

REFERENCES = {
    "kim2013": "Kim, H.-Y. (2013). Statistical notes for clinical researchers: Assessing normal distribution (2) using skewness and kurtosis. Restorative Dentistry & Endodontics, 38(1), 52–54. https://doi.org/10.5395/rde.2013.38.1.52",
    "ghasemi2012": "Ghasemi, A., & Zahediasl, S. (2012). Normality tests for statistical analysis: A guide for non-statisticians. International Journal of Endocrinology and Metabolism, 10(2), 486–489. https://doi.org/10.5812/ijem.3505",
    "midway2025": "Midway, S. R., & White, J. W. (2025). Testing for normality in regression models: Mistakes abound (but may not matter). Royal Society Open Science, 12(4), 241904. https://doi.org/10.1098/rsos.241904",
    "west1995": "West, S. G., Finch, J. F., & Curran, P. J. (1995). Structural equation models with nonnormal variables: Problems and remedies. Dalam R. H. Hoyle (Ed.), Structural equation modeling: Concepts, issues, and applications (hlm. 56–75). Sage.",
    "field2018": "Field, A. (2018). Discovering statistics using IBM SPSS Statistics (5th ed.). Sage.",
    "efron1993": "Efron, B., & Tibshirani, R. J. (1993). An introduction to the bootstrap. Chapman & Hall.",
    "boxcox1964": "Box, G. E. P., & Cox, D. R. (1964). An analysis of transformations. Journal of the Royal Statistical Society: Series B (Methodological), 26(2), 211–252. https://doi.org/10.1111/j.2517-6161.1964.tb00553.x",
    "yeojohnson2000": "Yeo, I.-K., & Johnson, R. A. (2000). A new family of power transformations to improve normality or symmetry. Biometrika, 87(4), 954–959. https://doi.org/10.1093/biomet/87.4.954",
    "dunn1964": "Dunn, O. J. (1964). Multiple comparisons using rank sums. Technometrics, 6(3), 241–252. https://doi.org/10.1080/00401706.1964.10490181",
    "hayes2007": "Hayes, A. F., & Cai, L. (2007). Using heteroskedasticity-consistent standard error estimators in OLS regression: An introduction and software implementation. Behavior Research Methods, 39(4), 709–722. https://doi.org/10.3758/BF03192961",
}

_BY_CHOSEN = {"bootstrap": ["efron1993"], "hc3": ["hayes2007"], "kruskal": ["field2018"],
              "mannwhitney": ["field2018"], "wilcoxon": ["field2018"], "spearman": ["field2018"],
              "kendall": ["field2018"]}
_BY_TRANSFORM = {"boxcox": "boxcox1964", "yeojohnson": "yeojohnson2000"}
_TEST_SYMBOL = {"shapiro": "W", "lilliefors": "D", "ks_classic": "D", "anderson": "A²",
                "jarque_bera": "JB", "dagostino": "K²"}
_TRANSFORM_NAME = {"log": "logaritma natural", "sqrt": "akar kuadrat", "reciprocal": "kebalikan (1/x)",
                   "boxcox": "Box-Cox", "yeojohnson": "Yeo-Johnson"}
_STATUS = {"ok": "tidak menunjukkan penyimpangan dari distribusi normal",
           "warn": "menunjukkan penyimpangan ringan dari distribusi normal",
           "bad": "menyimpang dari distribusi normal"}
_GOAL_TEST = {"ttest_ind": "uji-t independen", "ttest_paired": "uji-t berpasangan", "anova": "ANOVA satu arah"}
# Aturan keputusan per rentang n, sama dengan normality.decide_status.
_RULE = {
    "n<50": "Dengan α = {a} dan n kurang dari 50, keputusan memakai Shapiro-Wilk (Ghasemi & Zahediasl, 2012).",
    "50-300": ("Dengan α = {a} dan n antara 50 dan 300, keputusan memakai Shapiro-Wilk dan z-skewness/z-kurtosis "
               "(batas |z| < 3,29; Kim, 2013)."),
    ">300": ("Dengan α = {a} dan n di atas 300, keputusan memakai nilai skewness dan kurtosis (batas |skewness| < 2 "
             "dan |kurtosis| < 7; West dkk., 1995) ditambah Shapiro-Wilk."),
}


def fmt_num(x, digits=3):
    return f"{x:.{digits}f}".replace("-", "−").replace(".", ",")


def fmt_p(p):
    return "< 0,001" if p < 0.001 else fmt_num(p)


def _rel(p):
    return fmt_p(p) if p < 0.001 else f"= {fmt_p(p)}"


def _p_eq(p):
    return f"p {_rel(p)}"


def _num(v, digits=2):
    """Bilangan bulat tanpa desimal (df, U, W), selain itu dengan koma desimal."""
    return str(int(v)) if float(v).is_integer() else fmt_num(v, digits)


def _first_lower(s):
    return s[:1].lower() + s[1:]


def _subject(c):
    return c.get("subject") or c["label"]


def _main_test(c):
    return next((t for t in c["tests"] if t["id"] == "shapiro" and t.get("p") is not None), None) \
        or next((t for t in c["tests"] if t.get("p") is not None), None)


def _test_result(t):
    return f"{_TEST_SYMBOL.get(t['id'], t['name'])} = {fmt_num(t['stat'])}, {_p_eq(t['p'])}"


def _verdict(c, goal):
    """Kesimpulan normalitas sesuai status; status kuning karena kelompok besar tidak disebut penyimpangan ringan."""
    if c["verdict"].get("override") == "kelompok_besar":
        return (f"{_STATUS['bad']} (uji formal menolak normalitas); namun karena setiap kelompok berisi minimal "
                "30 responden serta skewness dan kurtosis masih dalam batas |skewness| < 2 dan |kurtosis| < 7, "
                f"{_GOAL_TEST.get(goal, 'uji parametrik')} cukup tahan (robust) terhadap penyimpangan ini")
    return _STATUS.get(c["verdict"]["status"], "belum dapat dinilai normalitasnya")


def _skipped(c, prefix):
    why = "jumlah datanya kurang dari 3" if c["n"] < 3 else "semua nilainya sama"
    s = f"{prefix}normalitas {_subject(c)} (n = {c['n']}) tidak dapat diuji karena {why}."
    return s[:1].upper() + s[1:]


def _after_par(c, what, goal):
    if c["verdict"]["status"] == "skipped":
        return _skipped(c, f"Setelah {what}, ")
    t = _main_test(c)
    if not t:
        return ""
    return (f"Setelah {what}, uji {t['name']} terhadap {_subject(c)} (n = {c['n']}) menghasilkan {_test_result(t)}, "
            f"sehingga, dengan aturan keputusan yang sama, data {_verdict(c, goal)}.")


def _check_par(c, goal, alpha):
    v = c["verdict"]
    if v["status"] == "skipped":
        return _skipped(c, "")
    t = _main_test(c)
    s = f"Uji normalitas dilakukan terhadap {_subject(c)} (n = {c['n']})"
    if t:
        s += f" menggunakan uji {t['name']}, dengan hasil {_test_result(t)}"
    m = c.get("moments") or {}
    if m.get("skew") is not None:
        s += (f"; skewness sebesar {fmt_num(m['skew'], 2)} (z = {fmt_num(m['z_skew'], 2)}) "
              f"dan kurtosis sebesar {fmt_num(m['kurt'], 2)} (z = {fmt_num(m['z_kurt'], 2)})")
    s += "."
    if v.get("rule") in _RULE:
        s += " " + _RULE[v["rule"]].format(a=fmt_num(alpha, 2))
    s += f" Berdasarkan aturan tersebut, data {_verdict(c, goal)}."
    if v["status"] in ("warn", "bad") and c.get("findings"):
        s += f" Penyebab utama penyimpangan adalah {_first_lower(c['findings'][0]['title'])}."
    return s


def _fix_par(state):
    parts = []
    fixes = state.get("fixes") or []
    if fixes:
        items = "; ".join(f"baris {f['row']} kolom {f['column']} dari {f['old']} menjadi {f['new']}" for f in fixes)
        parts.append(f"Perbaikan kesalahan input dilakukan pada {len(fixes)} sel, yaitu {items}.")
    ex = state.get("excluded") or {}
    if ex:
        items = "; ".join(f"baris {r} ({REASONS[k]})" for r, k in sorted(ex.items()))
        parts.append(f"Sebanyak {len(ex)} baris dikeluarkan dari analisis, yaitu {items}.")
    tr = state.get("transform")
    if tr:
        items = []
        for i, (name, info) in enumerate(tr.items()):
            t = f"{name} {'ditransformasi dengan' if i == 0 else 'dengan'} {_TRANSFORM_NAME.get(info['method'], info['method'])}"
            if info.get("lambda") is not None:
                t += f" (λ = {fmt_num(info['lambda'], 2)})"
            if info.get("reflected"):
                t += " setelah dicerminkan"
            if info.get("shift"):
                t += f" dan digeser sebesar {fmt_num(info['shift'], 2)}"
            items.append(t)
        parts.append("; ".join(items) + ".")
    return " ".join(parts)


def _stat_text(ch):
    """Simbol metode beserta df: t(df), F(df1, df2), U, W, H(df), r, ρ, τ, B (HC3/OLS: B; t(df))."""
    sym, v, df = ch.get("stat_name"), ch.get("stat"), ch.get("df")
    if not sym or v is None:
        return None
    dft = "" if df is None else "(" + ", ".join(_num(d) for d in (df if isinstance(df, list) else [df])) + ")"
    if sym == "B":
        return f"B = {fmt_num(v)}" + (f"; t{dft} = {fmt_num(ch['t'], 2)}" if ch.get("t") is not None else "")
    return f"{sym}{dft} = {_num(v, 1) if sym in ('U', 'W') else fmt_num(v, 2)}"


def _res_text(ch):
    res = [x for x in (_stat_text(ch),) if x]
    if ch.get("p") is not None:
        res.append(_p_eq(ch["p"]))
    if ch.get("ci"):
        d = 3 if ch.get("stat_name") == "B" else 2
        res.append(f"CI 95% [{fmt_num(ch['ci'][0], d)}; {fmt_num(ch['ci'][1], d)}]")
    if ch.get("effect") is not None and ch.get("effect") != ch.get("stat"):  # korelasi: koefisien = efeknya
        res.append(f"{ch.get('effect_name') or 'ukuran efek'} = {fmt_num(ch['effect'], 2)}")
    return ", ".join(res)


def _chosen_par(chosen):
    """chosen: satu hasil atau daftar hasil (satu per pasangan variabel) dengan metode yang sama."""
    chs = chosen if isinstance(chosen, list) else [chosen]
    s = f"Analisis dilanjutkan dengan {chs[0]['name']}"
    if len(chs) == 1:
        ch = chs[0]
        if ch.get("label"):
            s += f" untuk {ch['label']}"
        r = _res_text(ch)
        return s + (", dengan hasil " + r if r else "") + "."
    parts = [f"{c['label']}: {_res_text(c)}" if c.get("label") else _res_text(c) for c in chs]
    return s + ", dengan hasil " + "; ".join(parts) + "."


def _dunn_text(posthoc, alpha):
    out = []
    for y in dict.fromkeys(r["y"] for r in posthoc):
        sig = [r for r in posthoc if r["y"] == y and r["p_adj"] < alpha]
        head = f"Uji lanjut Dunn dengan koreksi Bonferroni (α = {fmt_num(alpha, 2)}) untuk {y} menunjukkan"
        if sig:
            items = "; ".join(f"{r['a']} dan {r['b']} (p terkoreksi {_rel(r['p_adj'])})" for r in sig)
            out.append(f"{head} pasangan kelompok yang berbeda bermakna: {items}.")
        else:
            out.append(f"{head} tidak ada pasangan yang berbeda bermakna.")
    return " ".join(out)


def build_report(state):
    checks = state.get("checks") or []
    chosen, tr = state.get("chosen"), state.get("transform")
    goal, alpha = state.get("goal"), state.get("alpha", 0.05)
    pars = [_check_par(c, goal, alpha) for c in checks]
    fix = _fix_par(state)
    if fix:
        pars.append(fix)
    what = " dan ".join(w for w, on in (("transformasi", tr), ("pengeluaran data", state.get("excluded"))) if on)
    if what:
        pars += [p for p in (_after_par(c, what, goal) for c in state.get("after") or []) if p]
    first = (chosen[0] if chosen else None) if isinstance(chosen, list) else chosen
    keys = ["kim2013", "ghasemi2012"]
    if chosen:
        par = _chosen_par(chosen)
        if first["id"] == "kruskal" and state.get("posthoc"):
            par += " " + _dunn_text(state["posthoc"], alpha)
            keys.append("dunn1964")
        pars.append(par)
    if goal == "regression":
        keys.append("midway2025")
    if any(c["verdict"].get("rule") == ">300" for c in checks):
        keys.append("west1995")
    if first:
        keys += _BY_CHOSEN.get(first["id"], [])
    keys += [_BY_TRANSFORM[i["method"]] for i in (tr or {}).values() if i["method"] in _BY_TRANSFORM]
    keys = list(dict.fromkeys(keys))
    return {"text": "\n\n".join(pars), "references": sorted(REFERENCES[k] for k in keys)}
