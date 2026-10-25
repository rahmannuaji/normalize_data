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
                      "chosen": {"id": "bootstrap", "name": "Bootstrap", "label": "X1", "stat": 0.48, "p": None, "ci": [0.31, 0.66], "effect": None}})
    t = r["text"]
    assert "W = 0,962" in t and "p = 0,001" in t and "87" in t and "bootstrap" in t.lower() and "[0,31; 0,66]" in t
    assert any("Kim" in ref for ref in r["references"]) and any("Efron" in ref for ref in r["references"])


def test_excluded_transform_effect():
    check = {"label": "Skor X", "n": 400,
             "tests": [{"id": "shapiro", "name": "Shapiro-Wilk", "stat": 0.9, "p": 0.0001, "rejected": True, "skipped_reason": None}],
             "moments": {"skew": 1.0, "kurt": 0.0, "z_skew": 8.0, "z_kurt": 1.0, "se_skew": .1, "se_kurt": .2},
             "verdict": {"status": "warn", "rule": ">300"}, "findings": []}
    r = build_report({"goal": "correlation", "checks": [check], "fixes": [], "excluded": {5: "salah_input"},
                      "transform": {"Y1": {"method": "boxcox", "lambda": 0.5, "shift": 0, "reflected": True}, "X1": {"method": "boxcox", "lambda": 0.58, "shift": 0, "reflected": False}},
                      "chosen": {"id": "spearman", "name": "Spearman", "label": "X dan Y", "stat": 0.44, "p": 0.0001,
                                 "ci": None, "effect": 0.44, "effect_name": "ρ"}})
    t = r["text"]
    assert "Salah input" in t and "Y1 ditransformasi dengan Box-Cox (λ = 0,50) setelah dicerminkan; X1 dengan Box-Cox (λ = 0,58)" in t and "ρ = 0,44" in t and "p < 0,001" in t
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
    assert "Setelah pengeluaran data, uji Shapiro-Wilk terhadap Skor X menghasilkan W = 0,123, p = 0,200, sehingga data berdistribusi normal." in t
    assert "masih belum berdistribusi normal" in build_report({**base, "after": [bad]})["text"]
    assert "Setelah" not in build_report({**base, "excluded": {}})["text"]


def test_chosen_list_reports_every_label():
    ch = [{"id": "bootstrap", "name": "Bootstrap", "label": f"X{i} → Y1", "stat": 0.4, "p": None, "ci": [0.1, 0.7], "effect": None} for i in (1, 2)]
    c = {"label": "Residual", "n": 50, "tests": [], "verdict": {"status": "bad", "rule": "n<50"}, "moments": {}, "findings": []}
    txt = build_report({"goal": "regression", "checks": [c], "fixes": [], "excluded": {}, "transform": None, "chosen": ch})["text"]
    assert "X1 → Y1: statistik" in txt and "X2 → Y1: statistik" in txt
