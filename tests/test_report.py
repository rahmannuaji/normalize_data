import re
import numpy as np, pandas as pd
from cekdata.remedies import alternative
from cekdata.report import fmt_num, fmt_p, build_report


def test_formatting():
    assert fmt_num(0.96234) == "0,962" and fmt_num(-1.1234, 2) == "−1,12"
    assert fmt_p(0.0004) == "< 0,001" and fmt_p(0.012) == "0,012"


def test_report_mentions_test_fix_and_remedy():
    check = {"label": "Residual regresi: X1 → Y1", "n": 147,
             "tests": [{"id": "shapiro", "name": "Shapiro-Wilk", "stat": 0.962, "p": 0.001, "rejected": True, "skipped_reason": None}],
             "moments": {"skew": -1.12, "kurt": 0.84, "z_skew": -5.6, "z_kurt": 2.1, "se_skew": .2, "se_kurt": .4},
             "verdict": {"status": "bad", "rule": "50-300"}, "findings": [{"id": "ceiling", "title": "Efek plafon"}]}
    r = build_report({"goal": "regression", "checks": [check], "fixes": [{"row": 87, "column": "S4", "old": 55, "new": 5}],
                      "excluded": {}, "transform": None,
                      "chosen": {"id": "bootstrap", "name": "Bootstrap", "label": "X1", "stat_name": "B", "stat": 0.48, "p": None, "ci": [0.31, 0.66], "effect": None}})
    t = r["text"]
    assert "W = 0,962" in t and "p = 0,001" in t and "87" in t and "bootstrap" in t.lower() and "B = 0,480, CI 95% [0,310; 0,660]" in t
    assert any("Kim" in ref for ref in r["references"]) and any("Efron" in ref for ref in r["references"])


def test_excluded_transform_effect():
    check = {"label": "Skor X", "n": 400,
             "tests": [{"id": "shapiro", "name": "Shapiro-Wilk", "stat": 0.9, "p": 0.0001, "rejected": True, "skipped_reason": None}],
             "moments": {"skew": 1.0, "kurt": 0.0, "z_skew": 8.0, "z_kurt": 1.0, "se_skew": .1, "se_kurt": .2},
             "verdict": {"status": "warn", "rule": ">300"}, "findings": []}
    r = build_report({"goal": "correlation", "checks": [check], "fixes": [], "excluded": {5: "salah_input"},
                      "transform": {"Y1": {"method": "boxcox", "lambda": 0.5, "shift": 0, "reflected": True}, "X1": {"method": "boxcox", "lambda": 0.58, "shift": 0, "reflected": False}},
                      "chosen": {"id": "spearman", "name": "Spearman", "label": "X dan Y", "stat_name": "ρ", "stat": 0.44, "p": 0.0001,
                                 "ci": None, "effect": 0.44, "effect_name": "ρ"}})
    t = r["text"]
    assert "Salah input" in t and "Y1 ditransformasi dengan Box-Cox (λ = 0,50) setelah dicerminkan; X1 dengan Box-Cox (λ = 0,58)" in t and t.count("0,44") == 1 and "ρ = 0,44, p < 0,001." in t
    refs = " ".join(r["references"])
    assert "West" in refs and "Box" in refs and "Field" in refs


def _chk(tid, name):
    return {"label": "Skor X", "n": 40,
            "tests": [{"id": tid, "name": name, "stat": 0.123, "p": 0.2, "rejected": False, "skipped_reason": None}],
            "moments": {"skew": None, "kurt": None, "z_skew": None, "z_kurt": None, "se_skew": None, "se_kurt": None},
            "verdict": {"status": "ok", "rule": "n<50"}, "findings": []}


def test_symbol_for_lilliefors_and_midway_reference_and_transform_name():
    r = build_report({"goal": "regression", "checks": [_chk("lilliefors", "Lilliefors")], "fixes": [], "excluded": {},
                      "transform": {"Y1": {"method": "sqrt", "lambda": None, "shift": 0, "reflected": False}}, "chosen": None})
    assert "D = 0,123" in r["text"] and "akar kuadrat" in r["text"]
    assert any("White" in x and "Royal Society Open Science" in x for x in r["references"])


def test_after_sentence_states_outcome():
    bad = {**_chk("shapiro", "Shapiro-Wilk"), "verdict": {"status": "bad", "rule": "n<50"}}
    ok = _chk("shapiro", "Shapiro-Wilk")
    base = {"goal": "regression", "checks": [bad], "fixes": [], "excluded": {5: "salah_input"}, "transform": None, "chosen": None}
    t = build_report({**base, "after": [ok]})["text"]
    assert ("Setelah pengeluaran data, uji Shapiro-Wilk terhadap Skor X (n = 40) menghasilkan W = 0,123, p = 0,200, "
            "sehingga, dengan aturan keputusan yang sama, data tidak menunjukkan penyimpangan dari distribusi normal.") in t
    last = lambda after: build_report({**base, "after": [after]})["text"].split("\n\n")[-1]
    assert "data menyimpang dari distribusi normal." in last(bad)
    assert "data menunjukkan penyimpangan ringan dari distribusi normal." in last({**ok, "verdict": {"status": "warn", "rule": "n<50"}})
    assert "Setelah" not in build_report({**base, "excluded": {}})["text"]


def test_chosen_list_reports_every_label():
    ch = [{"id": "bootstrap", "name": "Bootstrap", "label": f"X{i} → Y1", "stat_name": "B", "stat": 0.4, "p": None, "ci": [0.1, 0.7], "effect": None} for i in (1, 2)]
    c = {"label": "Residual", "n": 50, "tests": [], "verdict": {"status": "bad", "rule": "n<50"}, "moments": {}, "findings": []}
    txt = build_report({"goal": "regression", "checks": [c], "fixes": [], "excluded": {}, "transform": None, "chosen": ch})["text"]
    assert "X1 → Y1: B = 0,400" in txt and "X2 → Y1: B = 0,400" in txt and "statistik" not in txt



def test_chosen_clause_uses_each_methods_symbol_and_df():
    rng = np.random.default_rng(7); n = 60
    s = pd.DataFrame({"Y1": rng.exponential(size=n), "Y2": rng.exponential(size=n), "X1": rng.normal(size=n),
                      "__group": np.tile([1, 2, 3], 20)})
    V = lambda *ys, xs=(): [{"name": y, "role": "Y"} for y in ys] + [{"name": x, "role": "X"} for x in xs]
    txt = lambda res: build_report({"goal": "x", "checks": [], "chosen": res})["text"]
    reg = alternative(s, V("Y1", xs=["X1"]), "regression")
    boot, hc3 = reg["alternatives"][0], reg["alternatives"][1]
    assert re.search(r"B = −?\d,\d{3}, CI 95% \[−?\d,\d{3}; −?\d,\d{3}\], β terstandar = ", txt(boot))
    assert re.search(r"B = −?\d,\d{3}; t\(58\) = −?\d+,\d{2}, p [=<] ", txt(hc3))
    ind = alternative(s[s.__group != 3], V("Y1"), "ttest_ind")
    assert re.search(r"U = \d+, p [=<] ", txt(ind["alternatives"][0]))  # bilangan bulat, tanpa desimal
    assert re.search(r"t\(\d+,\d{2}\) = ", txt(ind["parametric"][0]))  # df Welch
    an = alternative(s, V("Y1"), "anova")
    assert "F(2, 57) = " in txt(an["parametric"][0]) and "H(2) = " in txt(an["alternatives"][0])
    pa = alternative(s, V("Y1", "Y2"), "ttest_paired")
    assert "t(59) = " in txt(pa["parametric"][0]) and re.search(r"W = \d+, p [=<] ", txt(pa["alternatives"][0]))
    co = alternative(s, V("Y1", xs=["X1"]), "correlation")
    sp, ke = (txt(r) for r in co["alternatives"])
    rho = re.search(r"ρ = (−?\d,\d\d)", sp).group(1)
    assert "untuk X1 dan Y1" in sp and sp.count(rho) == 1 and "τ = " in ke  # koefisien tidak diulang sebagai efek
    allt = [txt(r) for o in (reg, ind, an, pa, co) for r in o["parametric"] + o["alternatives"]]
    assert not any("statistik" in t for t in allt)


def test_kruskal_reports_dunn_pairs_and_reference():
    post = [{"y": "Y1", "a": "1", "b": "2", "p_adj": 0.0004}, {"y": "Y1", "a": "1", "b": "3", "p_adj": 0.2}]
    kr = {"id": "kruskal", "name": "Kruskal-Wallis", "label": "Y1: 1, 2, 3", "stat_name": "H", "stat": 12.3, "p": 0.002,
          "df": 2.0, "ci": None, "effect": 0.1, "effect_name": "ε²"}
    r = build_report({"goal": "anova", "checks": [], "chosen": kr, "posthoc": post, "alpha": 0.05})
    assert "H(2) = 12,30, p = 0,002, ε² = 0,10." in r["text"]
    assert "pasangan kelompok yang berbeda bermakna: 1 dan 2 (p terkoreksi < 0,001)." in r["text"] and "1 dan 3" not in r["text"]
    assert any(x.startswith("Dunn") for x in r["references"])
    none = build_report({"goal": "anova", "checks": [], "chosen": kr, "posthoc": [{**post[0], "p_adj": 0.3}], "alpha": 0.05})
    assert "untuk Y1 menunjukkan tidak ada pasangan yang berbeda bermakna." in none["text"]
    assert not any(x.startswith("Dunn") for x in build_report({"goal": "anova", "checks": [], "chosen": None, "posthoc": post})["references"])


def _c(status, rule, n=147, override=None, findings=()):
    return {"label": "Residual regresi: X1 → Y1", "subject": "residual model regresi X1 terhadap Y1", "n": n,
            "tests": [{"id": "shapiro", "name": "Shapiro-Wilk", "stat": 0.95, "p": 0.0004}],
            "moments": {"skew": -1.1, "kurt": 0.8, "z_skew": -5.6, "z_kurt": 2.1},
            "verdict": {"status": status, "rule": rule, "override": override}, "findings": list(findings)}


def test_normality_paragraph_states_rule_with_alpha_and_override_truthfully():
    t = build_report({"goal": "regression", "alpha": 0.01, "checks": [_c("bad", "50-300")]})["text"]
    assert ("terhadap residual model regresi X1 terhadap Y1 (n = 147) menggunakan uji Shapiro-Wilk, dengan hasil W = 0,950, p < 0,001; "
            "skewness sebesar −1,10 (z = −5,60)") in t
    assert ("Dengan α = 0,01 dan n antara 50 dan 300, keputusan memakai Shapiro-Wilk dan z-skewness/z-kurtosis "
            "(batas |z| < 3,29; Kim, 2013). Berdasarkan aturan tersebut, data menyimpang dari distribusi normal.") in t
    big = build_report({"goal": "ttest_ind", "checks": [_c("warn", "50-300", override="kelompok_besar")]})["text"]
    assert "ringan" not in big and "uji formal menolak normalitas" in big and "setiap kelompok berisi minimal 30 responden" in big
    assert "uji-t independen cukup tahan (robust) terhadap penyimpangan ini." in big
    big300 = build_report({"goal": "regression", "checks": [_c("ok", ">300", n=400)]})["text"]
    assert "Dengan α = 0,05 dan n di atas 300, keputusan memakai nilai skewness dan kurtosis (batas |skewness| < 2 dan |kurtosis| < 7; West dkk., 1995)" in big300


def test_cause_sentence_only_for_deviation_and_keeps_variable_case():
    f = [{"id": "unreversed_item", "title": "Butir P7 berlawanan arah dengan total Y1"}]
    assert "Penyebab utama penyimpangan adalah butir P7 berlawanan arah dengan total Y1." in build_report({"checks": [_c("bad", "50-300", findings=f)]})["text"]
    assert "Penyebab" not in build_report({"checks": [_c("ok", "50-300", findings=f)]})["text"]


def test_skipped_target_says_why_it_was_not_tested():
    c = {**_c("skipped", None, n=2), "subject": "Y1 pada kelompok L", "tests": [], "moments": None}
    assert build_report({"checks": [c]})["text"] == "Normalitas Y1 pada kelompok L (n = 2) tidak dapat diuji karena jumlah datanya kurang dari 3."
    same = {**c, "n": 30}
    assert build_report({"checks": [same]})["text"].endswith("tidak dapat diuji karena semua nilainya sama.")
