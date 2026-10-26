import pytest
import json
from cekdata import api
call = lambda f, **kw: json.loads(getattr(api, f)(json.dumps(kw)))
Y = {"name": "Y1", "role": "Y", "columns": [f"P{i}" for i in range(1, 11)], "combine": "sum", "reversed": [], "scale": None}
X = {"name": "X1", "role": "X", "columns": [f"S{i}" for i in range(1, 11)], "combine": "sum", "reversed": [], "scale": None}

def test_full_flow_on_example():
    s = call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet=None)
    assert s["n_rows"] == 150
    info = call("prepare", variables=[Y, X], group="JK")
    kinds = {(w["kind"], w.get("item") or w.get("column")) for w in info["warnings"]}
    assert ("negative_item_total", "P7") in kinds and ("out_of_range", "S4") in kinds
    assert info["n_dropped"] == 3
    call("set_cell", row=87, column="S4", value=5)
    call("prepare", variables=[{**Y, "reversed": ["P7"]}, X], group="JK")
    r = call("check", goal="regression", alpha=0.05)
    assert r["targets"][0]["verdict"]["status"] == "bad"
    alt = call("remedy", kind="alternative")
    assert alt["alternatives"][0]["id"] == "bootstrap"
    rep = call("report", chosen_id="bootstrap")
    assert "87" in rep["text"] and "bootstrap" in rep["text"].lower()

def test_goal_error_is_json_message():
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet=None)
    call("prepare", variables=[Y, X], group="JK")
    assert "minimal 3 kelompok" in call("check", goal="anova", alpha=0.05)["error"]

def test_exclude_without_reason_is_json_message():
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet=None)
    call("prepare", variables=[Y, X], group=None); call("check", goal="regression", alpha=0.05)
    assert "alasan" in call("remedy", kind="exclude", reasons={"12": ""})["error"]

def test_transform_and_exclude_return_before_after():
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet="")
    call("prepare", variables=[Y, X], group=None); call("check", goal="regression", alpha=0.05)
    t = call("remedy", kind="transform", method="sqrt")
    assert t["info"]["Y1"]["method"] == "sqrt" and t["before"][0]["n"] == t["after"][0]["n"] == 147
    e = call("remedy", kind="exclude", reasons={"12": "salah_input"})
    assert e["before"][0]["n"] == 147 and e["after"][0]["n"] == 146

def test_errors_are_indonesian_json():
    api._S.clear()
    assert call("prepare", variables=[Y, X], group=None)["error"].startswith("Data belum dimuat")
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet=None)
    assert call("prepare", variables=[{**Y, "columns": ["ZZ"]}], group=None)["error"] == 'Kolom "ZZ" tidak ditemukan.'
    assert call("set_cell", row=1, column="ZZ", value=1)["error"] == 'Kolom "ZZ" tidak ditemukan.'
    assert call("set_cell", row=999, column="S1", value=1)["error"] == "Baris 999 tidak ada di data."
    r = call("set_cell", row="a", column="S1", value=1)
    assert r["error"] == api._GENERIC and "TypeError" in r["detail"]  # pesan teknis hanya di detail (konsol)


@pytest.mark.filterwarnings("ignore")
def test_scipy_errors_on_constant_data_do_not_leak(tmp_path):
    import pandas as pd
    p = tmp_path / "c.csv"
    pd.DataFrame({"Y": [3] * 40, "G": [1, 2, 3, 4] * 10}).to_csv(p, sep=";", index=False)
    call("load_table", path=str(p))
    call("prepare", variables=[{**Y, "columns": ["Y"]}], group="G")
    call("check", goal="anova", alpha=0.05)
    assert call("remedy", kind="transform", method="boxcox")["error"] == "Semua nilai sama, jadi data tidak bisa ditransformasi."
    r = call("remedy", kind="alternative")
    assert r["error"] == api._GENERIC and "identical" in r["detail"]

def test_nan_becomes_null():
    assert json.loads(api._dumps({"a": float("nan"), "b": [float("inf")]})) == {"a": None, "b": [None]}


def _setup(goal="regression", **kw):
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet=None)
    call("prepare", variables=[{**Y, "reversed": ["P7"]}, X], group=None)
    return call("check", goal=goal, alpha=0.05)


def test_exclude_resets_stale_alternatives():
    _setup()
    call("remedy", kind="alternative")
    call("remedy", kind="exclude", reasons={"87": "salah_input"})
    rep = call("report", chosen_id="bootstrap")
    assert "bootstrap" not in rep["text"].lower()  # alternatif lama dibuang
    call("remedy", kind="alternative")
    after = call("report", chosen_id="bootstrap")["text"]
    assert "bootstrap" in after.lower() and "Responden" not in after and "Salah input" in after
    _setup()
    call("remedy", kind="alternative")
    before = call("report", chosen_id="bootstrap")["text"]
    ci = lambda t: t[t.index("CI 95%"):].split("]")[0]
    assert ci(before) != ci(after)


def test_transform_clear_and_report_omits_transform_when_chosen():
    _setup()
    call("remedy", kind="alternative")
    call("remedy", kind="transform", method="sqrt")
    assert "akar kuadrat" in call("report", chosen_id=None)["text"]
    assert "Y1 ditransformasi dengan akar kuadrat" in call("report", chosen_id=None)["text"]
    assert "akar kuadrat" not in call("report", chosen_id="bootstrap")["text"]
    assert call("remedy", kind="transform", method=None)["info"] is None
    assert "akar kuadrat" not in call("report", chosen_id=None)["text"]


def test_report_has_after_sentence_for_remedy():
    _setup()
    call("remedy", kind="transform", method="sqrt")
    assert "Setelah transformasi, uji Shapiro-Wilk" in call("report", chosen_id=None)["text"]


def test_set_cell_records_blank_and_int_and_dedupes():
    _setup()
    call("set_cell", row=20, column="P2", value=4)
    call("set_cell", row=87, column="S4", value=5)
    call("set_cell", row=87, column="S4", value=3)
    fixes = {(f["row"], f["column"]): f for f in api._S["fixes"]}
    assert fixes[(20, "P2")]["old"] == "kosong" and fixes[(87, "S4")]["old"] == 55 and fixes[(87, "S4")]["new"] == 3
    assert len(api._S["fixes"]) == 2
    call("prepare", variables=[Y, X], group=None)
    call("check", goal="regression", alpha=0.05)
    text = call("report", chosen_id=None)["text"]
    assert "kosong" in text and "5.0" not in text and "55.0" not in text


def test_excel_datetime_column(tmp_path):
    import pandas as pd
    f = tmp_path / "t.xlsx"
    pd.DataFrame({"tgl": pd.to_datetime(["2026-01-02", None]), "v": [1, 2]}).to_excel(f, index=False)
    s = call("load_table", path=str(f), sheet="")
    assert "error" not in s and s["n_rows"] == 2 and s["preview"][0][0].startswith("2026-01-02")


def test_excluded_row_warning_not_in_findings_after():
    _setup()
    r = call("remedy", kind="exclude", reasons={"87": "salah_input"})
    assert all(f["id"] != "data_error" for f in r["after"][0]["findings"])


def test_finding_rows_come_with_regression_table():
    f = next(f for f in _setup()["targets"][0]["findings"] if f["id"] == "outliers")
    assert f["table"]["columns"] == ["Baris", "Y1", "X1", "Residual terstandar", "Cook's D"]
    assert [r[0] for r in f["table"]["rows"]] == f["rows"]


def test_prepare_reports_group_sizes():
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet=None)
    g = call("prepare", variables=[Y, X], group="JK")["groups"]
    assert set(g) == {"L", "P"} and sum(g.values()) == 147
    assert call("prepare", variables=[Y, X], group=None)["groups"] is None


def test_ttest_ind_on_unfixed_example_lists_rows_per_group():
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet=None)
    call("prepare", variables=[Y, X], group="JK")
    r = call("check", goal="ttest_ind", alpha=0.05)
    assert "error" not in r
    hits = [t["label"] for t in r["targets"] if any(f["id"] == "data_error" for f in t["findings"])]
    assert len(hits) == 1


def test_verdict_override_flag():
    import numpy as np
    from cekdata import normality as nm
    x = np.random.default_rng(3).gamma(2.0, size=200)
    t = {"label": "g", "values": x, "rows": list(range(1, 201)), "groups_n": [100, 100]}
    assert nm.check_target({**t, "groups_n": None}, "ttest_ind", 0.05)["verdict"]["status"] == "bad"
    v = nm.check_target(t, "ttest_ind", 0.05)["verdict"]
    assert v["status"] == "warn" and v["override"] == "kelompok_besar"
    assert nm.check_target({**t, "groups_n": None}, "ttest_ind", 0.05)["verdict"]["override"] is None


def test_export_scores_full_rows_with_exclusion_and_transform():
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet="")
    call("prepare", variables=[Y, X], group=None); call("check", goal="regression", alpha=0.05)
    call("remedy", kind="exclude", reasons={"12": "salah_input"})
    call("remedy", kind="transform", method="sqrt")
    e = call("export_scores")
    assert e["columns"] == ["Baris", "Y1", "X1", "Y1 (transformasi)"]
    assert len(e["rows"]) == 146 and all(r[0] != 12 for r in e["rows"])
    assert call("export_scores", transformed=False)["columns"] == ["Baris", "Y1", "X1"]


def test_report_with_two_x_mentions_both_labels():
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet="")
    X2 = {**X, "name": "X2", "columns": [f"S{i}" for i in range(1, 6)]}
    call("prepare", variables=[Y, X, X2], group=None); call("check", goal="regression", alpha=0.05)
    call("remedy", kind="alternative")
    txt = call("report", chosen_id="bootstrap")["text"]
    assert "X1 → Y1: statistik" in txt and "X2 → Y1: statistik" in txt


def test_prepare_rejects_duplicate_empty_and_reserved_names():
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet=None)
    assert call("prepare", variables=[Y, {**X, "name": "Y1"}], group=None)["error"] == 'Nama variabel "Y1" dipakai lebih dari sekali.'
    assert call("prepare", variables=[Y, {**X, "name": "  "}], group=None)["error"] == "Nama variabel tidak boleh kosong."
    assert "__group" in call("prepare", variables=[Y, {**X, "name": "__group"}], group="JK")["error"]


def test_integer_valued_group_codes_read_as_integers(tmp_path):
    import numpy as np, pandas as pd
    rng = np.random.default_rng(1)
    p = tmp_path / "g.csv"
    pd.DataFrame({"Y": rng.normal(size=41), "G": [1, 2] * 20 + [None]}).to_csv(p, sep=";", index=False)  # sel kosong -> kolom float
    call("load_table", path=str(p))
    assert call("prepare", variables=[{**Y, "columns": ["Y"]}], group="G")["groups"] == {"1": 20, "2": 20}
    assert [t["label"] for t in call("check", goal="ttest_ind", alpha=0.05)["targets"]] == ["Y1 (kelompok 1)", "Y1 (kelompok 2)"]
    assert call("remedy", kind="alternative")["parametric"][0]["label"] == "Y1: 1 vs 2"
