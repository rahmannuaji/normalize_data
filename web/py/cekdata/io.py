import csv
import os
import re
import warnings as _w

import pandas as pd

from . import UserError

_NUM = r"^-?\d+,\d+$|^-?\d+$"
_MAX_ROWS_LISTED = 5


def _long_rows(path, sep, n_header):
    """Nomor baris data (1 = baris pertama setelah judul) yang punya lebih banyak kolom daripada judul."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        r = csv.reader(f, delimiter=sep)
        next(r, None)
        return [i for i, rec in enumerate(r, 1) if len(rec) > n_header]


def _read_csv(path):
    with open(path, encoding="utf-8-sig") as f:
        header = f.readline()
    # Pemisah dipilih dari baris header; sniffing pandas salah untuk satu kolom ("Y1" dikira berpemisah "1").
    # Header tanpa pemisah = satu kolom: pakai ";" agar nilai seperti "1,5" tidak terpecah.
    sep = next((c for c in (";", "\t", ",") if c in header), ";")
    try:
        with _w.catch_warnings(record=True) as caught:
            _w.simplefilter("always", pd.errors.ParserWarning)
            df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", skip_blank_lines=False, index_col=False)
    except pd.errors.ParserError as e:
        m = re.search(r"line (\d+)", str(e))
        where = f" di baris {int(m.group(1)) - 1}" if m else ""
        raise UserError(f"Format CSV tidak konsisten{where}. Periksa pemisah kolom (; atau ,).") from e
    warnings = []
    if any(issubclass(c.category, pd.errors.ParserWarning) for c in caught):
        rows = _long_rows(path, sep, len(df.columns))
        if rows:
            listed = ", ".join(map(str, rows[:_MAX_ROWS_LISTED]))
            more = f" dan {len(rows) - _MAX_ROWS_LISTED} lainnya" if len(rows) > _MAX_ROWS_LISTED else ""
            warnings.append(f"Baris {listed}{more} punya lebih banyak kolom daripada judul kolom; kolom tambahan diabaikan.")
    return df, warnings


def read_table(path, sheet=None):
    ext = os.path.splitext(path)[1].lower()
    warnings, sheets = [], []
    if ext == ".csv":
        df, warnings = _read_csv(path)
        # Baris kosong di tengah dipertahankan (nomor baris tetap sama); hanya yang di ujung dibuang.
        while len(df) and df.iloc[-1].isna().all():
            df = df.iloc[:-1]
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
            raise UserError(f"Sheet \"{sheet}\" tidak ditemukan. Sheet yang tersedia: {', '.join(sheets)}.")
        df = pd.read_excel(path, sheet_name=sheet or sheets[0], engine=engine)
    else:
        raise UserError("Format file belum didukung. Gunakan .csv, .xlsx, atau .xls.")
    return df, {"sheets": sheets, "warnings": warnings}


def table_summary(df, n_preview=10):
    head = df.head(n_preview).astype(object).where(df.head(n_preview).notna(), None)
    return {"columns": [str(c) for c in df.columns], "n_rows": len(df), "preview": head.values.tolist()}
