from cekdata.io import read_table, table_summary
import pandas as pd

def test_csv_indonesia_semicolon_decimal_comma_bom(tmp_path):
    p = tmp_path / "data.csv"
    p.write_bytes(b"\xef\xbb\xbf" + "No;P1;P2\n1;3,5;4\n2;4;5\n".encode("utf-8"))
    df, meta = read_table(str(p))
    assert list(df.columns) == ["No", "P1", "P2"]
    assert df["P1"].tolist() == [3.5, 4.0]
    assert any("P1" in w for w in meta["warnings"])

def test_excel_multi_sheet(tmp_path):
    p = tmp_path / "data.xlsx"
    with pd.ExcelWriter(p) as w:
        pd.DataFrame({"A": [1, 2]}).to_excel(w, sheet_name="Data", index=False)
        pd.DataFrame({"B": [3, 4, 5]}).to_excel(w, sheet_name="Lain", index=False)
    df, meta = read_table(str(p))
    assert meta["sheets"] == ["Data", "Lain"] and list(df.columns) == ["A"]
    df2, _ = read_table(str(p), sheet="Lain")
    assert df2["B"].tolist() == [3, 4, 5]

def test_summary_preview_none_for_nan():
    s = table_summary(pd.DataFrame({"A": [1.0, None]}))
    assert s == {"columns": ["A"], "n_rows": 2, "preview": [[1.0], [None]]}
