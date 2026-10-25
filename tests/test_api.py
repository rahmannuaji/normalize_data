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
    assert t["info"]["method"] == "sqrt" and t["before"][0]["n"] == t["after"][0]["n"] == 147
    e = call("remedy", kind="exclude", reasons={"12": "salah_input"})
    assert e["before"][0]["n"] == 147 and e["after"][0]["n"] == 146

def test_errors_are_indonesian_json():
    api._S.clear()
    assert call("prepare", variables=[Y, X], group=None)["error"].startswith("Data belum dimuat")
    call("load_table", path="web/contoh/kuesioner_psikologi.csv", sheet=None)
    assert call("prepare", variables=[{**Y, "columns": ["ZZ"]}], group=None)["error"].startswith("Terjadi kesalahan tak terduga: KeyError")

def test_nan_becomes_null():
    assert json.loads(api._dumps({"a": float("nan"), "b": [float("inf")]})) == {"a": None, "b": [None]}
