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
                      "transform": {"method": "boxcox", "lambda": 0.5, "shift": 0, "reflected": False},
                      "chosen": {"id": "spearman", "name": "Spearman", "label": "X dan Y", "stat": 0.44, "p": 0.0001,
                                 "ci": None, "effect": 0.44, "effect_name": "ρ"}})
    t = r["text"]
    assert "Salah input" in t and "0,5" in t and "ρ = 0,44" in t and "p < 0,001" in t
    refs = " ".join(r["references"])
    assert "West" in refs and "Box" in refs and "Field" in refs
