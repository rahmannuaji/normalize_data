import numpy as np, pandas as pd
from cekdata.prep import build_scores

def items_df():
    rng = np.random.default_rng(0)
    base = rng.integers(1, 6, size=60)
    near = lambda: np.clip(base + rng.integers(-1, 2, size=60), 1, 5)
    return pd.DataFrame({"P1": near(), "P2": near(), "P3": 6 - near()})  # P3 unfavorable

def spec(**kw):
    return {"name": "Y1", "role": "Y", "columns": ["P1", "P2", "P3"], "combine": "sum",
            "reversed": [], "scale": None, **kw}

def test_flags_unreversed_item():
    _, info = build_scores(items_df(), [spec()])
    assert any(w["kind"] == "negative_item_total" and w["item"] == "P3" for w in info["warnings"])

def test_reversing_fixes_flag_and_score():
    df = items_df()
    scores, info = build_scores(df, [spec(reversed=["P3"], scale=[1, 5])])
    assert not any(w["kind"] == "negative_item_total" for w in info["warnings"])
    assert scores["Y1"].tolist() == (df.P1 + df.P2 + 6 - df.P3).tolist()
    assert info["score_range"]["Y1"] == [3, 15]

def test_out_of_range_detected_with_inferred_scale():
    df = items_df(); df.loc[10, "P2"] = 55
    _, info = build_scores(df, [spec()])
    assert {"kind": "out_of_range", "row": 11, "column": "P2", "value": 55.0, "scale": [1, 5]} in info["warnings"]

def test_non_numeric_rows_dropped_and_counted():
    df = items_df().astype(object); df.loc[3, "P1"] = "-"; df.loc[7, "P1"] = "lima"
    scores, info = build_scores(df, [spec()])
    assert info["n_dropped"] == 2 and info["dropped_rows"] == [4, 8]
    assert {"kind": "non_numeric", "column": "P1", "count": 2} in info["warnings"]
    assert len(scores) == 58

def test_group_mean_and_single_column():
    df = items_df(); df["G"] = ["a", "b"] * 30
    scores, info = build_scores(df, [spec(combine="mean", scale=[1, 5]),
                                     {"name": "X1", "role": "X", "columns": ["P1"], "combine": "sum", "reversed": [], "scale": None}], group="G")
    assert list(scores.columns) == ["Y1", "X1", "__group"]
    assert info["score_range"] == {"Y1": [1, 5], "X1": None}


def test_item_total_correlation_excludes_the_item_itself():
    df = items_df()
    _, info = build_scores(df, [spec()])
    r = next(w["r"] for w in info["warnings"] if w["kind"] == "negative_item_total" and w["item"] == "P3")
    assert r == round(float(df["P3"].corr(df["P1"] + df["P2"])), 2)
