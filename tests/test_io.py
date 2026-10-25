from cekdata.io import read_table, table_summary
import pandas as pd
import pytest

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

def test_unsupported_extension_raises(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("a")
    with pytest.raises(ValueError, match="Format file belum didukung"):
        read_table(str(p))

def test_missing_sheet_raises_indonesian(tmp_path):
    p = tmp_path / "data.xlsx"
    pd.DataFrame({"A": [1]}).to_excel(p, sheet_name="Data", index=False)
    with pytest.raises(ValueError, match="tidak ditemukan"):
        read_table(str(p), sheet="Tidak")


def _csv(tmp_path, text):
    p = tmp_path / "d.csv"
    p.write_text(text, encoding="utf-8")
    return read_table(str(p))[0]

def test_single_column_csv(tmp_path):
    df = _csv(tmp_path, "Y1\n3\n5\n7\n")
    assert list(df.columns) == ["Y1"] and df["Y1"].tolist() == [3, 5, 7]

def test_single_column_interior_blank_kept_as_nan(tmp_path):
    df = _csv(tmp_path, "Y1\n3\n\n5\n")
    assert len(df) == 3 and pd.isna(df["Y1"].iloc[1])

def test_trailing_blank_lines_dropped(tmp_path):
    assert len(_csv(tmp_path, "Y1\n3\n5\n\n\n")) == 2
    assert len(_csv(tmp_path, "A;B\n1;2\n;\n3;4\n;\n")) == 3

def test_comma_separated(tmp_path):
    df = _csv(tmp_path, "A,B\n1,2\n")
    assert list(df.columns) == ["A", "B"] and len(df) == 1

def test_single_column_decimal_comma(tmp_path):
    df = _csv(tmp_path, "Y1\n1,5\n2,5\n")
    assert list(df.columns) == ["Y1"] and df["Y1"].tolist() == [1.5, 2.5]

@pytest.mark.filterwarnings("ignore::pandas.errors.ParserWarning")
def test_extra_fields_do_not_become_index(tmp_path):
    # Baris lebih panjang dari header: kolom kelebihan dibuang, nilai tidak bergeser jadi indeks.
    df = _csv(tmp_path, "A,B\n1,2,3\n4,5,6\n")
    assert df["A"].tolist() == [1, 4] and df["B"].tolist() == [2, 5]
