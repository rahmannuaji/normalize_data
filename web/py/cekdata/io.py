import os
import pandas as pd

_NUM = r"^-?\d+,\d+$|^-?\d+$"


def read_table(path, sheet=None):
    ext = os.path.splitext(path)[1].lower()
    warnings, sheets = [], []
    if ext == ".csv":
        df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]):
                continue
            s = df[c].dropna().astype(str).str.strip()
            if len(s) and s.str.match(_NUM).all() and s.str.contains(",").any():
                df[c] = pd.to_numeric(df[c].astype(str).str.strip().str.replace(",", ".", regex=False), errors="coerce")
                warnings.append(f"Kolom {c} memakai koma desimal. Sudah dibaca sebagai angka.")
    elif ext in (".xlsx", ".xls"):
        engine = "openpyxl" if ext == ".xlsx" else "xlrd"
        sheets = pd.ExcelFile(path, engine=engine).sheet_names
        if sheet is not None and sheet not in sheets:
            raise ValueError(f"Sheet \"{sheet}\" tidak ditemukan. Sheet yang tersedia: {', '.join(sheets)}.")
        df = pd.read_excel(path, sheet_name=sheet or sheets[0], engine=engine)
    else:
        raise ValueError("Format file belum didukung. Gunakan .csv, .xlsx, atau .xls.")
    return df, {"sheets": sheets, "warnings": warnings}


def table_summary(df, n_preview=10):
    head = df.head(n_preview).astype(object).where(df.head(n_preview).notna(), None)
    return {"columns": [str(c) for c in df.columns], "n_rows": len(df), "preview": head.values.tolist()}
