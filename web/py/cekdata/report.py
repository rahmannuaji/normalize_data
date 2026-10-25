"""Laporan Bab IV berbahasa Indonesia formal + daftar rujukan APA 7."""
from .remedies import REASONS

REFERENCES = {
    "kim2013": "Kim, H.-Y. (2013). Statistical notes for clinical researchers: Assessing normal distribution (2) using skewness and kurtosis. Restorative Dentistry & Endodontics, 38(1), 52–54. https://doi.org/10.5395/rde.2013.38.1.52",
    "ghasemi2012": "Ghasemi, A., & Zahediasl, S. (2012). Normality tests for statistical analysis: A guide for non-statisticians. International Journal of Endocrinology and Metabolism, 10(2), 486–489. https://doi.org/10.5812/ijem.3505",
    "midway2025": "Midway, S. R. (2025). Data analysis in R. https://bookdown.org/steve_midway/DAR/",
    "west1995": "West, S. G., Finch, J. F., & Curran, P. J. (1995). Structural equation models with nonnormal variables: Problems and remedies. In R. H. Hoyle (Ed.), Structural equation modeling: Concepts, issues, and applications (pp. 56–75). Sage.",
    "field2018": "Field, A. (2018). Discovering statistics using IBM SPSS Statistics (5th ed.). Sage.",
    "efron1993": "Efron, B., & Tibshirani, R. J. (1993). An introduction to the bootstrap. Chapman & Hall.",
    "boxcox1964": "Box, G. E. P., & Cox, D. R. (1964). An analysis of transformations. Journal of the Royal Statistical Society: Series B (Methodological), 26(2), 211–252. https://doi.org/10.1111/j.2517-6161.1964.tb00553.x",
    "yeojohnson2000": "Yeo, I.-K., & Johnson, R. A. (2000). A new family of power transformations to improve normality or symmetry. Biometrika, 87(4), 954–959. https://doi.org/10.1093/biomet/87.4.954",
    "dunn1964": "Dunn, O. J. (1964). Multiple comparisons using rank sums. Technometrics, 6(3), 241–252. https://doi.org/10.1080/00401706.1964.10490181",
    "hayes2007": "Hayes, A. F., & Cai, L. (2007). Using heteroskedasticity-consistent standard error estimators in OLS regression: An introduction and software implementation. Behavior Research Methods, 39(4), 709–722. https://doi.org/10.3758/BF03192961",
}

_BY_CHOSEN = {"bootstrap": ["efron1993"], "hc3": ["hayes2007"], "kruskal": ["dunn1964", "field2018"],
              "mannwhitney": ["field2018"], "wilcoxon": ["field2018"], "spearman": ["field2018"],
              "kendall": ["field2018"]}
_BY_TRANSFORM = {"boxcox": "boxcox1964", "yeojohnson": "yeojohnson2000"}
_TEST_SYMBOL = {"shapiro": "W", "ks": "D", "lilliefors": "D", "ad": "A²", "dagostino": "K²", "jb": "JB"}
_STATUS = {"ok": "tidak menunjukkan penyimpangan dari distribusi normal",
           "warn": "menunjukkan penyimpangan ringan dari distribusi normal",
           "bad": "menyimpang dari distribusi normal"}


def fmt_num(x, digits=3):
    return f"{x:.{digits}f}".replace("-", "−").replace(".", ",")


def fmt_p(p):
    return "< 0,001" if p < 0.001 else fmt_num(p)


def _p_eq(p):
    return f"p {fmt_p(p)}" if p < 0.001 else f"p = {fmt_p(p)}"


def _check_par(c):
    t = next((t for t in c["tests"] if t["id"] == "shapiro" and t.get("p") is not None), None) \
        or next((t for t in c["tests"] if t.get("p") is not None), None)
    s = f"Uji normalitas dilakukan terhadap {c['label']} (n = {c['n']})"
    if t:
        sym = _TEST_SYMBOL.get(t["id"], "statistik")
        s += f" menggunakan uji {t['name']}, dengan hasil {sym} = {fmt_num(t['stat'])}, {_p_eq(t['p'])}"
    s += f". Berdasarkan hasil tersebut, data {_STATUS.get(c['verdict']['status'], 'belum dapat dinilai normalitasnya')}"
    m = c.get("moments") or {}
    if m.get("skew") is not None:
        s += (f"; skewness sebesar {fmt_num(m['skew'], 2)} (z = {fmt_num(m['z_skew'], 2)}) "
              f"dan kurtosis sebesar {fmt_num(m['kurt'], 2)} (z = {fmt_num(m['z_kurt'], 2)})")
    s += "."
    if c.get("findings"):
        s += f" Penyebab utama penyimpangan adalah {c['findings'][0]['title'].lower()}."
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
        s = f"Data ditransformasi dengan metode {tr['method']}"
        if tr.get("lambda") is not None:
            s += f" (λ = {fmt_num(tr['lambda'], 2)})"
        if tr.get("reflected"):
            s += " setelah dilakukan pencerminan"
        if tr.get("shift"):
            s += f" dan penggeseran sebesar {fmt_num(tr['shift'], 2)}"
        parts.append(s + ".")
    return " ".join(parts)


def _chosen_par(ch):
    s = f"Analisis dilanjutkan dengan {ch['name']}"
    if ch.get("label"):
        s += f" untuk {ch['label']}"
    res = []
    if ch.get("stat") is not None:
        res.append(f"statistik = {fmt_num(ch['stat'], 2)}")
    if ch.get("p") is not None:
        res.append(_p_eq(ch["p"]))
    if ch.get("ci"):
        res.append(f"CI 95% [{fmt_num(ch['ci'][0], 2)}; {fmt_num(ch['ci'][1], 2)}]")
    if ch.get("effect") is not None:
        res.append(f"{ch.get('effect_name') or 'ukuran efek'} = {fmt_num(ch['effect'], 2)}")
    return s + (", dengan hasil " + ", ".join(res) if res else "") + "."


def build_report(state):
    checks = state.get("checks") or []
    chosen, tr = state.get("chosen"), state.get("transform")
    pars = [_check_par(c) for c in checks]
    fix = _fix_par(state)
    if fix:
        pars.append(fix)
    if chosen:
        pars.append(_chosen_par(chosen))
    keys = ["kim2013", "ghasemi2012"]
    if state.get("goal") == "regression":
        keys.append("midway2025")
    if any(c["verdict"].get("rule") == ">300" for c in checks):
        keys.append("west1995")
    if chosen:
        keys += _BY_CHOSEN.get(chosen["id"], [])
    if tr and tr["method"] in _BY_TRANSFORM:
        keys.append(_BY_TRANSFORM[tr["method"]])
    keys = list(dict.fromkeys(keys))
    return {"text": "\n\n".join(pars), "references": sorted(REFERENCES[k] for k in keys)}
