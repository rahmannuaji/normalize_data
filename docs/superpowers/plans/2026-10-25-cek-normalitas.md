# Normalin — Rencana Pembuatan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Website statis berbahasa Indonesia yang memeriksa normalitas data skripsi (terutama kuesioner Likert), menunjukkan penyebab ketidaknormalan, dan menjalankan solusi yang sah, seluruhnya di browser.

**Architecture:** Semua logika statistik ada di paket Python murni `cekdata` (di `web/py/cekdata/`). Paket ini diuji dengan pytest di komputer lokal, lalu dijalankan di browser lewat Pyodide. Tampilan berupa HTML/CSS/JS biasa tanpa build step. JS memanggil Python hanya lewat `cekdata.api`, dengan JSON string masuk dan JSON string keluar. State analisis (DataFrame) disimpan di modul `api`.

**Tech Stack:** Python 3.12, numpy, pandas, scipy, statsmodels, openpyxl, xlrd · Pyodide v0.27.7 (CDN jsDelivr; kalau versi ini tidak ada, pakai rilis 0.27.x terakhir) · Plotly.js 2.35.2 (`plotly.js-dist-min`) · pytest · font Plus Jakarta Sans · ikon Lucide (disalin sebagai sprite SVG).

**Spec:** `docs/2026-10-25-cek-normalitas-design.md` · produk: `PRODUCT.md` · brand: `docs/brand-guidelines.md` · kontrak arah desain: `.impeccable/surfaces/web-index-html.md` · acuan tampilan: `mockup/mockup.html`

## Global Constraints

- Semua teks yang dilihat pengguna berbahasa Indonesia. Angka di tampilan dan laporan memakai koma desimal ("0,962"), p kecil ditulis "< 0,001".
- Data tidak boleh dikirim ke server mana pun: tidak ada `fetch`/`XMLHttpRequest` yang membawa data pengguna, dan tidak ada analytics.
- Taraf signifikansi default 0,05, bisa diganti 0,01.
- Tidak ada fitur yang menghapus data otomatis sampai normal, menambah data, atau mengecilkan sampel.
- Status hijau/kuning/merah selalu disertai ikon dan teks.
- Tata letak berfungsi di lebar 375 px tanpa scroll horizontal pada halaman (tabel lebar boleh digeser di dalam wadahnya).
- Nomor baris yang ditampilkan ke pengguna = indeks baris data (0-based, tanpa header) + 1.
- Shapiro-Wilk minimal n = 3. Untuk n > 5000 tampilkan catatan "p-value Shapiro-Wilk kurang akurat untuk n > 5000".
- Bootstrap: 5.000 sampel ulang, seed 2026.
- **Nama produk: Normalin** (judul tab "Normalin — cek normalitas data skripsi"). Copy mengikuti `docs/brand-guidelines.md` §4: sapaan "kamu", menenangkan, dan tanpa istilah yang dilarang ("menormalkan data", "data valid", "seamless").
- **Desain (berlaku untuk Task 9–13):** sebelum mengedit UI, baca `docs/brand-guidelines.md`, kontrak arah di `.impeccable/surfaces/web-index-html.md`, dan `C:/Users/Asus/.claude/plugins/cache/impeccable/impeccable/4.7.0/skills/impeccable/reference/craft-floor.md`. Warna, radius, spasi, dan tipe hanya lewat custom property di `:root` `web/style.css` yang nilainya sama persis dengan brand guidelines (tidak ada hex mentah di luar `:root`). Tidak ada emoji sebagai ikon; pakai `<svg><use href="assets/icons.svg#nama"/></svg>`. Ikon dekoratif `aria-hidden="true"`, tombol ikon-saja wajib `aria-label`. Target sentuh ≥ 44px, fokus terlihat (outline 2px indigo, offset 2px), dan `prefers-reduced-motion` mematikan transisi. Tanpa gradien, glass, atau bayangan tebal.
- **Footer:** "dibuat oleh {AUTHOR}" dengan `const AUTHOR = ""` di `app.js`; baris footer tidak ditampilkan selama kosong. Nama pembuat jangan diisi sendiri.
- Ukuran data yang harus lancar: sampai sekitar 10.000 baris × 200 kolom. Pyodide berjalan di thread utama; pindahkan ke Web Worker hanya bila langkah mana pun membeku lebih dari 2 detik pada ukuran ini.

## Review Focus

1. **CSV dari Excel versi Indonesia** (pemisah `;`, koma desimal, BOM UTF-8) harus terbaca sebagai angka, bukan teks → test di Task 1.
2. **Kolom bervariasi nol** (semua responden menjawab 5) harus menghasilkan status `skipped` dengan pesan jelas, bukan crash atau pembagian dengan nol → test di Task 3.
3. **n sangat kecil** (n < 8, atau kelompok kecil) membuat uji yang butuh n lebih besar ditandai `skipped`, sementara uji lain tetap jalan → test di Task 3.
4. **Sel non-angka** di kolom terpilih ("-", "lima", spasi) diubah jadi kosong, barisnya dikeluarkan, dan jumlahnya dilaporkan per kolom → test di Task 2.
5. **Kolom kelompok tidak cocok dengan tujuan** (uji-t independen butuh tepat 2 kelompok, ANOVA ≥ 3, uji-t berpasangan butuh 2 variabel Y) memunculkan pesan bahasa Indonesia, bukan traceback → test di Task 4 dan Task 8.

---

## Struktur berkas

```
.gitignore
pytest.ini                  # pythonpath = web/py ; testpaths = tests
requirements-dev.txt
README.md
tools/make_examples.py      # pembuat dataset contoh (deterministik)
web/
  index.html  style.css     # :root berisi token dari docs/brand-guidelines.md
  assets/logo.svg  assets/favicon.svg  assets/icons.svg   # logo kurva lonceng, sprite Lucide
  engine.js                 # memuat Pyodide + paket cekdata, call(name, args)
  app.js                    # state UI, navigasi langkah, render tiap langkah
  charts.js                 # histogram, Q-Q, P-P, boxplot (Plotly)
  contoh/kuesioner_psikologi.csv  contoh/pretest_posttest.csv
  py/cekdata/
    __init__.py
    io.py         # baca CSV/Excel
    prep.py       # skor variabel, balik item, pemeriksaan data
    target.py     # apa yang diuji normalitasnya per tujuan analisis
    normality.py  # semua uji, momen, aturan status, data grafik
    diagnose.py   # penyebab ketidaknormalan
    remedies.py   # uji alternatif, bootstrap, Dunn, transformasi, eksklusi
    report.py     # format angka Indonesia, teks laporan, rujukan
    api.py        # pintu masuk JSON untuk JS, menyimpan state
tests/
  test_io.py test_prep.py test_normality.py test_target.py
  test_diagnose.py test_remedies.py test_report.py test_api.py
```

---

### Task 1: Penyiapan proyek dan pembacaan file (`io.py`)

**Files:**
- Create: `.gitignore`, `pytest.ini`, `requirements-dev.txt`, `web/py/cekdata/__init__.py` (kosong), `web/py/cekdata/io.py`
- Test: `tests/test_io.py`

**Interfaces:**
- Produces:
  - `read_table(path: str, sheet: str | None = None) -> tuple[pd.DataFrame, dict]`; meta = `{"sheets": list[str], "warnings": list[str]}`
  - `table_summary(df: pd.DataFrame, n_preview: int = 10) -> dict` → `{"columns": list[str], "n_rows": int, "preview": list[list]}` (NaN → `None`)

- [ ] **Step 1: Siapkan repo**

```bash
git init
```
`.gitignore`: `__pycache__/`, `.pytest_cache/`, `.venv/`, `.impeccable/config.local.json`. `pytest.ini`:
```ini
[pytest]
pythonpath = web/py
testpaths = tests
```
`requirements-dev.txt`: `numpy>=1.26`, `pandas>=2.2`, `scipy>=1.14`, `statsmodels>=0.14`, `openpyxl>=3.1`, `xlrd>=2.0`, `pytest>=8`. Lalu jalankan `python -m pip install -r requirements-dev.txt`.

- [ ] **Step 2: Tulis test yang gagal**

```python
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
```

- [ ] **Step 3: Jalankan, pastikan gagal**

Run: `pytest tests/test_io.py -v` → FAIL (`ModuleNotFoundError: cekdata.io`)

- [ ] **Step 4: Implementasi `read_table` dan `table_summary`**

CSV: `pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")`. Lalu untuk tiap kolom bertipe object yang semua nilai tidak-kosongnya cocok dengan `^-?\d+,\d+$|^-?\d+$` dan minimal satu mengandung koma: ganti `,` → `.`, `pd.to_numeric`, lalu tambahkan warning `"Kolom {c} memakai koma desimal. Sudah dibaca sebagai angka."`. `.xlsx` memakai openpyxl, `.xls` memakai xlrd. Daftar sheet dari `pd.ExcelFile(path).sheet_names`; default sheet pertama. Ekstensi lain → `ValueError("Format file belum didukung. Gunakan .csv, .xlsx, atau .xls.")`.

- [ ] **Step 5: Jalankan, pastikan lulus**

Run: `pytest tests/test_io.py -v` → 3 passed

- [ ] **Step 6: Commit**

```bash
git add .gitignore pytest.ini requirements-dev.txt web/py/cekdata tests/test_io.py
git commit -m "feat: baca CSV/Excel termasuk format Excel Indonesia"
```

---

### Task 2: Skor variabel dan pemeriksaan data (`prep.py`)

**Files:**
- Create: `web/py/cekdata/prep.py`
- Test: `tests/test_prep.py`

**Interfaces:**
- Consumes: DataFrame dari `read_table`.
- Produces:
  - Variable spec (dict): `{"name": str, "role": "Y" | "X", "columns": list[str], "combine": "sum" | "mean", "reversed": list[str], "scale": [min, max] | None}`
  - `build_scores(df: pd.DataFrame, variables: list[dict], group: str | None = None) -> tuple[pd.DataFrame, dict]`
    - scores: satu kolom per `name` (+ kolom `"__group"` bila ada `group`), index = index asli df, hanya baris lengkap.
    - info: `{"n_used": int, "n_dropped": int, "dropped_rows": list[int], "warnings": list[dict], "score_range": {name: [min, max] | None}}`
    - jenis warning: `{"kind": "non_numeric", "column", "count"}`, `{"kind": "out_of_range", "row", "column", "value"}`, `{"kind": "negative_item_total", "variable", "item", "r"}`

- [ ] **Step 1: Tulis test yang gagal**

```python
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
    assert {"kind": "out_of_range", "row": 11, "column": "P2", "value": 55.0} in info["warnings"]

def test_non_numeric_rows_dropped_and_counted():
    df = items_df().astype(object); df.loc[3, "P1"] = "-"; df.loc[7, "P1"] = "lima"
    scores, info = build_scores(df, [spec()])
    assert info["n_dropped"] == 2 and info["dropped_rows"] == [4, 8]
    assert {"kind": "non_numeric", "column": "P1", "count": 2} in info["warnings"]
    assert len(scores) == 58
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `pytest tests/test_prep.py -v` → FAIL (import error)

- [ ] **Step 3: Implementasi `build_scores`**

Aturan yang tidak tertebak dari test:
- Konversi: `pd.to_numeric(errors="coerce")` per kolom terpilih. Sel non-kosong yang menjadi NaN dihitung sebagai `non_numeric`.
- Skala bila `scale` None (hanya untuk variabel dengan ≥ 2 kolom): kumpulkan semua nilai item variabel itu, ambil nilai unik yang muncul di ≥ 1% sel, lalu skala = [min, max] dari nilai-nilai tersebut. Nilai di luar skala menjadi `out_of_range`, tetapi tidak diubah.
- Balik item: `min + max − nilai`, memakai skala di atas.
- `negative_item_total`: korelasi Pearson item dengan jumlah item lainnya (corrected item-total, setelah item dibalik) < 0; `r` dibulatkan 2 desimal.
- `score_range`: untuk `sum` = [k·min, k·max]; untuk `mean` = [min, max]; variabel satu kolom tanpa `scale` → None.

- [ ] **Step 4: Jalankan, pastikan lulus**

Run: `pytest tests/test_prep.py -v` → 4 passed

- [ ] **Step 5: Commit**

```bash
git add web/py/cekdata/prep.py tests/test_prep.py
git commit -m "feat: skor variabel dari item, balik item, deteksi salah input"
```

---

### Task 3: Uji normalitas, momen, dan aturan status (`normality.py`)

**Files:**
- Create: `web/py/cekdata/normality.py`
- Test: `tests/test_normality.py`

**Interfaces:**
- Produces:
  - `moments(x: np.ndarray) -> dict` → `{"skew", "kurt", "se_skew", "se_kurt", "z_skew", "z_kurt"}` (skew = G1, kurt = G2 kurtosis berlebih, sama seperti SPSS)
  - `run_tests(x: np.ndarray, alpha: float = 0.05) -> list[dict]`, masing-masing `{"id", "name", "stat", "p", "rejected": bool | None, "skipped_reason": str | None}`; urutan id: `shapiro, lilliefors, ks_classic, anderson, jarque_bera, dagostino, skew_kurt`
  - `decide_status(n, sw_p, skew, kurt, z_skew, z_kurt, goal, groups_n, alpha) -> tuple[str, str]` → (`"ok"|"warn"|"bad"`, `"n<50"|"50-300"|">300"`)
  - `check_target(target: dict, goal: str, alpha: float = 0.05) -> dict` → `{"label", "n", "tests", "moments", "verdict": {"status", "rule", "reason", "rejected", "total"}, "plot": {"values", "qq": {"theoretical", "sample", "rows"}, "pp": {"expected", "observed"}}, "notes": list[str]}`. `target` mengikuti bentuk dari Task 4 (minimal `label`, `values`, `rows`, `groups_n`).

- [ ] **Step 1: Tulis test yang gagal**

```python
import numpy as np, pytest
from scipy.stats import norm, expon
from cekdata.normality import moments, run_tests, decide_status, check_target

Q40 = (np.arange(1, 41) - 0.5) / 40

def test_shapiro_matches_r_reference():
    # R: shapiro.test(58:72) -> W = 0.96359, p-value = 0.7545
    t = run_tests(np.arange(58, 73, dtype=float))[0]
    assert t["id"] == "shapiro"
    assert t["stat"] == pytest.approx(0.96359, abs=1e-4) and t["p"] == pytest.approx(0.7545, abs=1e-3)

def test_se_formulas_n147():
    m = moments(norm.ppf((np.arange(1, 148) - 0.5) / 147))
    assert m["se_skew"] == pytest.approx(0.2000, abs=1e-3)
    assert m["se_kurt"] == pytest.approx(0.3975, abs=1e-3)

def test_all_seven_tests_present():
    assert [t["id"] for t in run_tests(norm.ppf(Q40))] == [
        "shapiro", "lilliefors", "ks_classic", "anderson", "jarque_bera", "dagostino", "skew_kurt"]

def test_small_n_skips_some_tests():
    tests = {t["id"]: t for t in run_tests(np.array([1.0, 2.0, 2.5, 4.0, 7.0]))}
    assert tests["shapiro"]["p"] is not None
    assert tests["dagostino"]["skipped_reason"] is not None

@pytest.mark.parametrize("args,expected", [
    ((30, 0.01, 0.5, 0.1, 1.2, 0.1, "regression", None), ("bad", "n<50")),
    ((30, 0.20, 0.5, 0.1, 1.2, 0.1, "regression", None), ("ok", "n<50")),
    ((147, 0.001, -1.12, 0.84, -5.6, 2.1, "regression", None), ("bad", "50-300")),
    ((147, 0.02, -0.4, 0.3, -2.0, 0.8, "regression", None), ("warn", "50-300")),
    ((500, 0.0001, 0.6, 1.0, 5.5, 4.6, "regression", None), ("warn", ">300")),
    ((500, 0.0001, 2.3, 1.0, 21.0, 4.6, "regression", None), ("bad", ">300")),
    ((500, 0.30, 0.1, 0.1, 0.9, 0.5, "regression", None), ("ok", ">300")),
    ((147, 0.001, -1.12, 0.84, -5.6, 2.1, "ttest_ind", [70, 77]), ("warn", "50-300")),
    ((60, 0.001, -1.12, 0.84, -3.6, 2.1, "ttest_ind", [25, 35]), ("bad", "50-300")),
])
def test_decide_status(args, expected):
    assert decide_status(*args, alpha=0.05) == expected

def test_constant_values_skipped():
    r = check_target({"label": "Y1", "values": np.full(30, 5.0), "rows": list(range(1, 31)), "groups_n": None}, "normality_only")
    assert r["verdict"]["status"] == "skipped"

def test_check_target_exponential_bad_with_plot_data():
    x = expon.ppf(Q40)
    r = check_target({"label": "Y1", "values": x, "rows": list(range(1, 41)), "groups_n": None}, "normality_only")
    assert r["verdict"]["status"] == "bad"
    assert len(r["plot"]["qq"]["sample"]) == 40 and sorted(r["plot"]["qq"]["rows"]) == list(range(1, 41))
```

- [ ] **Step 2: Jalankan, pastikan gagal**

Run: `pytest tests/test_normality.py -v` → FAIL (import error)

- [ ] **Step 3: Implementasi `moments` dan `run_tests`**

- `skew = scipy.stats.skew(x, bias=False)`, `kurt = scipy.stats.kurtosis(x, bias=False)`; `se_skew = sqrt(6n(n−1)/((n−2)(n+1)(n+3)))`, `se_kurt = 2·se_skew·sqrt((n²−1)/((n−3)(n+5)))`.
- Pemanggilan: shapiro → `scipy.stats.shapiro` (n ≥ 3); lilliefors → `statsmodels.stats.diagnostic.lilliefors(x, dist="norm", pvalmethod="table")` (n ≥ 4); ks_classic → `scipy.stats.kstest(x, "norm", args=(mean, sd_ddof1))` (n ≥ 4); anderson → `statsmodels.stats.diagnostic.normal_ad` (n ≥ 8); jarque_bera → `scipy.stats.jarque_bera` (n ≥ 8); dagostino → `scipy.stats.normaltest` (n ≥ 8, jika n < 20 tambahkan catatan "kurang akurat untuk n < 20"); skew_kurt: `stat` = `"skew; kurt"`, `p` = None, `rejected` = max(|z_skew|, |z_kurt|) ≥ batas (1,96 bila n < 50; 3,29 bila 50–300) atau, bila n > 300, |skew| ≥ 2 atau |kurt| ≥ 7.
- Uji di bawah n minimal: `skipped_reason = "Butuh minimal {k} data"`.
- Nama tampilan: "Shapiro-Wilk", "Kolmogorov-Smirnov (Lilliefors)", "Kolmogorov-Smirnov klasik (SPSS)", "Anderson-Darling", "Jarque-Bera", "D'Agostino-Pearson K²", "Skewness & kurtosis (z)".

- [ ] **Step 4: Implementasi `decide_status`**

```
n < 50:        bad jika sw_p < alpha, selain itu ok
50 ≤ n ≤ 300:  ok jika sw_p ≥ alpha; warn jika max(|z_skew|,|z_kurt|) < 3,29; selain itu bad
n > 300:       bad jika |skew| ≥ 2 atau |kurt| ≥ 7; warn jika sw_p < alpha; selain itu ok
Lalu: bad → warn jika goal ∈ {ttest_ind, ttest_paired, anova} dan min(groups_n) ≥ 30
      dan |skew| < 2 dan |kurt| < 7   (rule tetap sama)
```

- [ ] **Step 5: Implementasi `check_target`**

- `skipped` dengan reason "Semua nilai sama, normalitas tidak bisa diuji." bila sd = 0, atau "Data kurang dari 3." bila n < 3.
- `reason` berupa satu kalimat Indonesia yang menyebut uji utama, p, dan aturan yang dipakai, misalnya "Untuk n antara 50 dan 300 dipakai Shapiro-Wilk ditambah z-skewness/kurtosis (batas 3,29; Kim, 2013)."
- `rejected`/`total` = jumlah uji yang menolak dari uji yang tidak di-skip.
- Q-Q: nilai distandarkan lalu diurutkan, dengan `rows` mengikuti urutan itu; teoretis = `norm.ppf((i − 0.375)/(n + 0.25))`. P-P: `observed = norm.cdf(z_sorted)`, `expected = (i − 0.5)/n`.
- `notes` memuat catatan n > 5000 (lihat Global Constraints).

- [ ] **Step 6: Jalankan, pastikan lulus**

Run: `pytest tests/test_normality.py -v` → semua passed

- [ ] **Step 7: Commit**

```bash
git add web/py/cekdata/normality.py tests/test_normality.py
git commit -m "feat: tujuh uji normalitas dan aturan status"
```

---

### Task 4: Apa yang diuji per tujuan analisis (`target.py`)

**Files:**
- Create: `web/py/cekdata/target.py`
- Test: `tests/test_target.py`

**Interfaces:**
- Consumes: `scores`, `variables` dari Task 2.
- Produces:
  - `GOALS = ("correlation", "regression", "ttest_ind", "ttest_paired", "anova", "normality_only")`
  - `class GoalError(ValueError)`, pesannya berbahasa Indonesia dan siap ditampilkan
  - `build_targets(scores: pd.DataFrame, variables: list[dict], goal: str) -> list[dict]`; tiap target: `{"label": str, "kind": "variable"|"residual"|"difference"|"group", "values": np.ndarray, "rows": list[int], "groups_n": list[int] | None, "y": str | None, "model": dict | None}`; untuk regresi `model = {"std_resid": ndarray, "cooks": ndarray, "mahal_p": ndarray | None, "fitted": ndarray}`

| goal | target |
|---|---|
| correlation, normality_only | tiap variabel → kind `variable`, label = nama variabel |
| regression | tiap Y: OLS `Y ~ semua X` (statsmodels) → residual; label `"Residual regresi: X1, X2 → Y1"`; `mahal_p` dari X (chi², df = jumlah X) bila jumlah X ≥ 2 |
| ttest_ind | tiap Y × tiap level `__group` → kind `group`; label `"Y1 (kelompok L)"`; `groups_n` = n kedua kelompok |
| ttest_paired | `Y2 − Y1` (dua Y pertama) → kind `difference`; label `"Selisih Y2 − Y1"` |
| anova | tiap Y: residual `Y ~ C(__group)` → kind `residual`; label `"Residual ANOVA: Y1 ~ kelompok"`; `groups_n` per level |

- [ ] **Step 1: Tulis test yang gagal**

```python
import numpy as np, pandas as pd, pytest
from cekdata.target import build_targets, GoalError

V = [{"name": "Y1", "role": "Y"}, {"name": "X1", "role": "X"}, {"name": "X2", "role": "X"}]

def scores(groups):
    rng = np.random.default_rng(3); n = 60
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    return pd.DataFrame({"Y1": 1 + x1 + 0.5 * x2 + rng.normal(size=n), "X1": x1, "X2": x2,
                         "__group": np.resize(groups, n)}, index=range(10, 10 + n))

def test_regression_residuals():
    [t] = build_targets(scores(["L", "P"]), V, "regression")
    assert t["kind"] == "residual" and t["label"] == "Residual regresi: X1, X2 → Y1"
    assert abs(t["values"].mean()) < 1e-9 and t["rows"][0] == 11
    assert t["model"]["mahal_p"] is not None

def test_ttest_ind_two_groups():
    ts = build_targets(scores(["L", "P"]), V, "ttest_ind")
    assert [t["label"] for t in ts] == ["Y1 (kelompok L)", "Y1 (kelompok P)"] and ts[0]["groups_n"] == [30, 30]

def test_ttest_ind_rejects_three_groups():
    with pytest.raises(GoalError, match="tepat 2 kelompok"):
        build_targets(scores(["A", "B", "C"]), V, "ttest_ind")

def test_anova_rejects_two_groups():
    with pytest.raises(GoalError, match="minimal 3 kelompok"):
        build_targets(scores(["L", "P"]), V, "anova")

def test_paired_needs_two_y():
    with pytest.raises(GoalError, match="dua variabel Y"):
        build_targets(scores(["L", "P"]), V, "ttest_paired")
```

- [ ] **Step 2: Jalankan, pastikan gagal** — `pytest tests/test_target.py -v` → FAIL
- [ ] **Step 3: Implementasi `build_targets`** sesuai tabel di atas. Pesan GoalError: "Uji-t independen butuh kolom kelompok dengan tepat 2 kelompok (sekarang {k}).", "ANOVA butuh kolom kelompok dengan minimal 3 kelompok (sekarang {k}).", "Uji-t berpasangan butuh dua variabel Y (Y1 = sebelum, Y2 = sesudah).", "Regresi butuh minimal satu variabel X.", "Tujuan ini butuh kolom kelompok." (bila `__group` tidak ada).
- [ ] **Step 4: Jalankan, pastikan lulus** — `pytest tests/test_target.py -v` → 5 passed
- [ ] **Step 5: Commit** — `git commit -m "feat: target normalitas per tujuan analisis"` (add `target.py`, `test_target.py`)

---

### Task 5: Penyebab ketidaknormalan (`diagnose.py`)

**Files:**
- Create: `web/py/cekdata/diagnose.py`
- Test: `tests/test_diagnose.py`

**Interfaces:**
- Consumes: target (Task 4), `moments` (Task 3), `info["score_range"]` dan `info["warnings"]` (Task 2).
- Produces: `diagnose(target: dict, m: dict, score_range: list | None, y_values: np.ndarray | None, prep_warnings: list[dict]) -> list[dict]`; tiap temuan `{"id", "severity": "high"|"medium"|"low", "title", "detail", "rows": list[int]}`, diurutkan high → low. `y_values` = skor Y asli (untuk target residual), atau `target["values"]` untuk target lain.

Aturan (ambang adalah keputusan saya, kecuali ceiling ≥ 15% yang berasal dari spec):

| id | kondisi | severity |
|---|---|---|
| `data_error` | ada warning `out_of_range` | high |
| `unreversed_item` | ada warning `negative_item_total` | high |
| `ceiling` / `floor` | `score_range` ada dan ≥ 15% `y_values` ≥ max − 0,1·(max−min) (atau ≤ min + 0,1·rentang) | high |
| `skew_left` / `skew_right` | skew ≤ −0,5 / ≥ 0,5 | medium (high bila \|skew\| ≥ 1) |
| `heavy_tails` / `light_tails` | kurt ≥ 1 / ≤ −1 | medium |
| `outliers` | IQR 1,5× atau \|z\| > 3; untuk regresi juga \|std_resid\| > 3, Cook's D > 4/n, `mahal_p` < 0,001 | medium |
| `bimodal` | koefisien bimodalitas Sarle `(G1²+1)/(G2 + 3(n−1)²/((n−2)(n−3)))` > 0,555 | medium |
| `low_variety` | jumlah nilai unik ≤ 5 | low |

`title` dan `detail` berbahasa Indonesia dan memuat angkanya, contoh: "Efek plafon: 24% responden memberi skor hampir maksimal".

- [ ] **Step 1: Tulis test yang gagal**

```python
import numpy as np
from scipy.stats import norm
from cekdata.diagnose import diagnose
from cekdata.normality import moments

def tgt(x): return {"label": "Y1", "kind": "variable", "values": x, "rows": list(range(1, len(x) + 1)), "groups_n": None, "model": None}
ids = lambda f: [d["id"] for d in f]

def test_ceiling_found_with_rows():
    x = np.r_[np.full(30, 48.0), np.linspace(20, 44, 70)]
    f = diagnose(tgt(x), moments(x), [10, 50], x, [])
    c = next(d for d in f if d["id"] == "ceiling")
    assert c["severity"] == "high" and c["rows"] == list(range(1, 31))

def test_outlier_rows():
    x = np.r_[norm.ppf((np.arange(1, 100) - 0.5) / 99), 6.0]
    f = diagnose(tgt(x), moments(x), None, x, [])
    assert 100 in next(d for d in f if d["id"] == "outliers")["rows"]

def test_bimodal():
    x = np.r_[norm.ppf((np.arange(1, 51) - .5) / 50) - 3, norm.ppf((np.arange(1, 51) - .5) / 50) + 3]
    assert "bimodal" in ids(diagnose(tgt(x), moments(x), None, x, []))

def test_normal_has_no_findings():
    x = norm.ppf((np.arange(1, 101) - .5) / 100)
    assert diagnose(tgt(x), moments(x), None, x, []) == []

def test_prep_warnings_become_high_findings_first():
    x = norm.ppf((np.arange(1, 101) - .5) / 100)
    w = [{"kind": "out_of_range", "row": 87, "column": "S4", "value": 55.0}]
    f = diagnose(tgt(x), moments(x), None, x, w)
    assert f[0]["id"] == "data_error" and f[0]["rows"] == [87]
```

- [ ] **Step 2: Jalankan, pastikan gagal** — `pytest tests/test_diagnose.py -v`
- [ ] **Step 3: Implementasi `diagnose`** sesuai tabel.
- [ ] **Step 4: Jalankan, pastikan lulus** — 5 passed
- [ ] **Step 5: Commit** — `git commit -m "feat: diagnosis penyebab ketidaknormalan"`

---

### Task 6: Solusi (`remedies.py`)

**Files:**
- Create: `web/py/cekdata/remedies.py`
- Test: `tests/test_remedies.py`

**Interfaces:**
- Consumes: `scores`, `variables` (Task 2), `GOALS` (Task 4).
- Produces:
  - `alternative(scores: pd.DataFrame, variables: list[dict], goal: str) -> dict` → `{"parametric": list[dict], "alternatives": list[dict], "posthoc": list[dict] | None}`; tiap hasil `{"id", "name", "label", "stat", "p", "ci": [lo, hi] | None, "effect": float | None}`
  - `bootstrap_ols(y: np.ndarray, X: np.ndarray, names: list[str], n_boot: int = 5000, seed: int = 2026) -> dict` → `{"names", "coef", "ci_low", "ci_high"}` (termasuk intercept bernama `"Konstanta"`)
  - `dunn(values: np.ndarray, groups: np.ndarray) -> list[dict]` → `{"a", "b", "z", "p", "p_adj"}`
  - `transform(x: np.ndarray, method: str) -> tuple[np.ndarray, dict]`; method ∈ `{"log", "sqrt", "reciprocal", "boxcox", "yeojohnson"}`; info `{"method", "lambda", "shift", "reflected"}`
  - `REASONS = {"salah_input": "Salah input", "menjawab_asal": "Responden menjawab asal", "di_luar_populasi": "Di luar populasi penelitian"}`
  - `exclude_rows(scores: pd.DataFrame, reasons: dict[int, str]) -> pd.DataFrame` (key = nomor baris tampilan)

| goal | parametric | alternatives (id) |
|---|---|---|
| correlation | Pearson per pasangan Y×X | `spearman`, `kendall` (Kendall ditandai `recommended` bila nilai unik/n < 0,5) |
| regression | OLS per Y | `bootstrap` (bootstrap_ols, CI persentil), `hc3` (statsmodels `cov_type="HC3"`) |
| ttest_ind | uji-t Welch | `mannwhitney` (effect = rank-biserial) |
| ttest_paired | uji-t berpasangan | `wilcoxon` |
| anova | ANOVA satu arah | `kruskal` + `posthoc` = `dunn(...)` |
| normality_only | – | – (alternatif kosong) |

- [ ] **Step 1: Tulis test yang gagal**

```python
import numpy as np, pandas as pd, pytest
from cekdata.remedies import alternative, bootstrap_ols, dunn, transform, exclude_rows

def test_bootstrap_recovers_slope_and_is_deterministic():
    rng = np.random.default_rng(5); x = rng.normal(size=200); y = 2 + 0.5 * x + rng.normal(scale=.3, size=200)
    a = bootstrap_ols(y, x[:, None], ["X1"]); b = bootstrap_ols(y, x[:, None], ["X1"])
    assert a == b and a["names"] == ["Konstanta", "X1"]
    assert a["ci_low"][1] < 0.5 < a["ci_high"][1]

def test_dunn_bonferroni():
    v = np.r_[np.arange(10), np.arange(10) + 20, np.arange(10) + 40.0]; g = np.repeat(["A", "B", "C"], 10)
    res = dunn(v, g)
    assert len(res) == 3 and all(r["p_adj"] == pytest.approx(min(1, r["p"] * 3)) for r in res)
    assert next(r for r in res if {r["a"], r["b"]} == {"A", "C"})["p_adj"] < 0.05

def test_boxcox_shifts_nonpositive():
    t, info = transform(np.array([0.0, 1, 2, 3, 10]), "boxcox")
    assert info["shift"] == 1 and np.isfinite(t).all() and info["lambda"] is not None

def test_left_skew_is_reflected_for_log():
    _, info = transform(np.array([1.0, 8, 9, 9, 10, 10, 10]), "log")
    assert info["reflected"] is True

def test_exclude_requires_valid_reason():
    s = pd.DataFrame({"Y1": [1.0, 2, 3]})
    assert exclude_rows(s, {2: "salah_input"}).index.tolist() == [0, 2]
    with pytest.raises(ValueError, match="alasan"):
        exclude_rows(s, {2: ""})

def test_alternative_regression_has_bootstrap_and_hc3():
    rng = np.random.default_rng(1); x = rng.normal(size=80)
    s = pd.DataFrame({"Y1": x + rng.exponential(size=80), "X1": x})
    out = alternative(s, [{"name": "Y1", "role": "Y"}, {"name": "X1", "role": "X"}], "regression")
    assert [a["id"] for a in out["alternatives"]][:2] == ["bootstrap", "hc3"]
```

- [ ] **Step 2: Jalankan, pastikan gagal** — `pytest tests/test_remedies.py -v`
- [ ] **Step 3: Implementasi** sesuai tabel. Detail yang tidak ditentukan test:
  - Semua fungsi mengembalikan list/float Python, bukan ndarray (agar bisa dibandingkan dan di-JSON-kan).
  - Bootstrap: resampling kasus (baris), `np.random.default_rng(seed)`, CI persentil 2,5% dan 97,5%.
  - Dunn: `z = (R̄a − R̄b) / sqrt((N(N+1)/12 − Σ(t³−t)/(12(N−1))) · (1/na + 1/nb))`, `p = 2(1 − Φ(|z|))`, `p_adj = min(1, p·m)` dengan m = jumlah pasangan.
  - Transformasi: bila skew < 0 dan method ∈ {log, sqrt, reciprocal, boxcox}, refleksikan dulu `x' = max(x) + 1 − x`. Bila min ≤ 0 untuk log/reciprocal/boxcox, geser `x + (1 − min)`. sqrt hanya digeser bila min < 0. yeojohnson memakai `scipy.stats.yeojohnson` tanpa refleksi atau geser.
  - Pesan error eksklusi: "Setiap baris yang dikeluarkan wajib punya alasan."
- [ ] **Step 4: Jalankan, pastikan lulus** — 6 passed
- [ ] **Step 5: Commit** — `git commit -m "feat: uji alternatif, bootstrap, Dunn, transformasi, eksklusi beralasan"`

---

### Task 7: Laporan (`report.py`)

**Files:**
- Create: `web/py/cekdata/report.py`
- Test: `tests/test_report.py`

**Interfaces:**
- Consumes: hasil `check_target` (Task 3), `diagnose` (Task 5), `alternative`/`transform` (Task 6).
- Produces:
  - `fmt_num(x: float, digits: int = 3) -> str`, `fmt_p(p: float) -> str`
  - `REFERENCES: dict[str, str]` (key: `kim2013`, `ghasemi2012`, `midway2025`, `west1995`, `field2018`, `efron1993`, `boxcox1964`, `yeojohnson2000`, `dunn1964`, `hayes2007`) dalam format APA 7
  - `build_report(state: dict) -> dict` → `{"text": str, "references": list[str]}`. Isi state: `{"goal", "checks": list[check_target result + "findings"], "fixes": list[{"row","column","old","new"}], "excluded": dict[int, str], "transform": dict | None, "chosen": dict | None}` (`chosen` = satu hasil dari `alternative`)

- [ ] **Step 1: Tulis test yang gagal**

```python
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
```

- [ ] **Step 2: Jalankan, pastikan gagal** — `pytest tests/test_report.py -v`
- [ ] **Step 3: Implementasi.** `fmt_num` memakai tanda minus "−" (U+2212) dan koma desimal. Teks laporan terdiri dari paragraf: (1) uji normalitas pada apa, n, uji utama dengan statistik dan p, status, skewness/z, dan penyebab utama (judul temuan pertama); (2) perbaikan data/eksklusi beserta alasannya/transformasi beserta λ, hanya bila ada; (3) analisis yang dipilih dan hasilnya. Rujukan yang selalu ada: kim2013, ghasemi2012; midway2025 bila goal = regression; west1995 bila rule ">300"; ditambah rujukan sesuai `chosen.id`/transform (bootstrap → efron1993, hc3 → hayes2007, kruskal → dunn1964 + field2018, mannwhitney/wilcoxon/spearman/kendall → field2018, boxcox → boxcox1964, yeojohnson → yeojohnson2000).
- [ ] **Step 4: Jalankan, pastikan lulus** — 2 passed
- [ ] **Step 5: Commit** — `git commit -m "feat: laporan bahasa Indonesia dan rujukan"`

---

### Task 8: API JSON, dataset contoh, dan uji ujung-ke-ujung (`api.py`)

**Files:**
- Create: `web/py/cekdata/api.py`, `tools/make_examples.py`, `web/contoh/kuesioner_psikologi.csv`, `web/contoh/pretest_posttest.csv`
- Test: `tests/test_api.py`

**Interfaces:**
- Consumes: semua modul di atas.
- Produces (setiap fungsi menerima satu JSON string dan mengembalikan JSON string; NaN/inf → `null`, tipe numpy → Python; error yang diharapkan (`GoalError`, `ValueError`) → `{"error": "<pesan Indonesia>"}`):
  - `load_table('{"path", "sheet"}')` → `table_summary` + `{"sheets", "warnings"}`
  - `set_cell('{"row", "column", "value"}')` → `{"ok": true}`; mengubah data mentah dan mencatat ke `fixes`
  - `prepare('{"variables", "group"}')` → info dari `build_scores` + `{"preview": scores 10 baris}`
  - `check('{"goal", "alpha"}')` → `{"targets": [check_target result + "findings"]}`
  - `remedy('{"kind": "alternative"}')` → hasil `alternative`; `'{"kind": "transform", "method"}'` → `{"info", "before": check, "after": check}`; `'{"kind": "exclude", "reasons": {"12": "menjawab_asal"}}'` → `{"before", "after"}`
  - `report('{"chosen_id": str | null}')` → `build_report`
- Transformasi berlaku untuk variabel Y (regresi/uji-t/ANOVA) atau semua variabel (korelasi/normality_only), lalu target dibangun ulang.

- [ ] **Step 1: Tulis `tools/make_examples.py`** (seed 2026). Kuesioner: 150 baris, kolom `No, P1..P10, S1..S10, JK`. Y-item `clip(round(4.2 + 0.8·Ly + N(0, 0.6)), 1, 5)` agar ada efek plafon; `P7 = 6 − nilai` (unfavorable yang belum dibalik); X-item `clip(round(3.4 + 0.9·Lx + N(0, 0.6)), 1, 5)` dengan `Ly = 0.5·Lx + N(0, 0.85)`; `S4` baris ke-87 (indeks 86) = 55; P2 kosong di baris 20, 45, 101; `JK` bergantian L/P. Pretest–posttest: 40 baris, `Pre ~ N(60, 10)`, `Post = Pre + Gamma(2, 3)` dibulatkan. Simpan sebagai CSV dengan pemisah `;` dan koma desimal (format Excel Indonesia). Jalankan: `python tools/make_examples.py`.

- [ ] **Step 2: Tulis test yang gagal**

```python
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
```

- [ ] **Step 3: Jalankan, pastikan gagal** — `pytest tests/test_api.py -v`
- [ ] **Step 4: Implementasi `api.py`** dengan state modul `_S` (`raw`, `variables`, `group`, `scores`, `info`, `goal`, `alpha`, `checks`, `fixes`, `excluded`, `transform`, `alternatives`). `check` menyimpan `goal`/`alpha` dan mereset `excluded`/`transform`. Memanggil `prepare`/`check`/`remedy`/`report` sebelum `load_table` → `{"error": "Data belum dimuat. Masukkan data di langkah 1."}`. Bila status target bukan `bad` pada contoh, naikkan konstanta 4.2 di generator sampai `bad` (dataset contoh dibuat untuk memperagakan jalur merah).
- [ ] **Step 5: Jalankan seluruh test** — `pytest -v` → semua passed
- [ ] **Step 6: Commit** — `git add web/py/cekdata/api.py tools web/contoh tests/test_api.py && git commit -m "feat: API JSON dan dataset contoh"`

---

### Task 9: Kerangka halaman, aset brand, dan mesin Pyodide

**Files:**
- Create: `web/index.html`, `web/style.css`, `web/engine.js`, `web/app.js`, `web/assets/logo.svg`, `web/assets/favicon.svg`, `web/assets/icons.svg`

**Interfaces:**
- Consumes: `cekdata.api` (Task 8).
- Produces:
  - `engine.js`: `export async function ready(): Promise<void>`, `export async function call(name: string, args: object): Promise<object>` (melempar `Error(pesan)` bila hasil berisi `error`), `export async function writeFile(name: string, bytes: Uint8Array): Promise<string>` (menulis ke `/tmp/<name>` lalu mengembalikan path)
  - `app.js`: `state` (objek), `go(step: number)`, `showError(msg: string)`; elemen per langkah `<section class="page" data-step="0..7">`

- [ ] **Step 0: Aset brand.**
  - `logo.svg`: tanda berupa kotak indigo #3B5BDB 28×28 bersudut 8px berisi satu kurva lonceng putih (path, stroke 2,5px, tanpa fill), ditambah wordmark "Normalin" dalam `<text>` Plus Jakarta Sans 800 berwarna #1B2333.
  - `favicon.svg`: tanda saja.
  - `icons.svg`: sprite `<symbol id="…" viewBox="0 0 24 24">` yang path-nya disalin dari Lucide v0.460.0 (lisensi ISC, cantumkan di komentar sprite), stroke `currentColor` 2px, untuk id: `upload, keyboard, flask-conical, lock, arrow-right, arrow-left, circle-check, triangle-alert, circle-x, circle-slash, circle-help, info, link, trending-up, scale, repeat, puzzle, search, file-spreadsheet, rotate-ccw, copy, download, printer, ban, chevron-down, plus`.
  - Semua emoji di mockup dipetakan ke ikon ini.
- [ ] **Step 1: Pindahkan HTML/CSS dari `mockup/mockup.html`** ke `index.html` + `style.css`: header, stepper, delapan `section`, token warna, dan kelas komponen. Token di `:root` diganti dengan nilai `docs/brand-guidelines.md` (nama variabel: `--bg, --surface, --surface-sunken, --ink, --muted, --line, --brand, --brand-dark, --brand-soft, --ok, --ok-soft, --warn, --warn-soft, --bad, --bad-soft, --info, --radius-btn, --radius-card, --space-xs..--space-2xl, --font-body, --font-report`). Logo teks diganti `assets/logo.svg` dan favicon dipasang. First viewport beranda harus persis seperti blok FIRST VIEWPORT di kontrak arah (histogram diberi label "data contoh"). Isi langkah 1–7 dikosongkan menjadi wadah (`<div id="step1">`, dst.) yang nanti diisi `app.js`. Beranda dipertahankan. Badge "MOCKUP" dan semua data palsu dihapus. Skrip: `<script type="module" src="app.js">`, Pyodide `https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js`, Plotly `https://cdn.jsdelivr.net/npm/plotly.js-dist-min@2.35.2/plotly.min.js`.
- [ ] **Step 2: Implementasi `engine.js`.** Mulai memuat saat halaman dibuka: `loadPyodide`, `loadPackage(["numpy","pandas","scipy","statsmodels","openpyxl","micropip"])`, `micropip.install("xlrd")`, lalu fetch setiap berkas di `const PY_FILES = ["__init__.py","io.py","prep.py","target.py","normality.py","diagnose.py","remedies.py","report.py","api.py"]` dari `py/cekdata/` dan tulis ke `/home/pyodide/cekdata/`, lalu `import cekdata.api`. Selama memuat, tampilkan bar di bawah header berisi "Menyiapkan mesin statistik… (sekali saja, sekitar 15 MB)". Tombol "Lanjut" di langkah 1 nonaktif sampai `ready()` selesai.
- [ ] **Step 3: Implementasi navigasi di `app.js`.** `go(step)` mengikuti perilaku mockup. Langkah > 1 tidak bisa diklik sebelum data dimuat. `showError` menampilkan `.note.bad` di atas langkah aktif.
- [ ] **Step 4: Verifikasi di browser.** Jalankan `python -m http.server 8000 -d web`, buka `http://localhost:8000`. Expected: beranda tampil seperti mockup, bar pemuatan muncul lalu hilang, dan tidak ada error di console. Di console, `await (await import('./engine.js')).call('check', {goal: 'regression', alpha: 0.05})` sebelum data dimuat harus melempar Error dengan pesan bahasa Indonesia, bukan traceback. Cek di lebar 375 px: tidak ada scroll horizontal.
- [ ] **Step 5: Commit** — `git commit -m "feat: kerangka halaman dan pemuatan Pyodide"`

---

### Task 10: Langkah 1–2 (data dan variabel)

**Files:**
- Modify: `web/app.js`, `web/index.html`, `web/style.css`

**Interfaces:**
- Consumes: `call("load_table")`, `call("set_cell")`, `call("prepare")`, `writeFile`.
- Produces: `state.table` (hasil load_table), `state.variables` (list spec Task 2), `state.group`, `state.prep` (hasil prepare).

- [ ] **Step 1: Langkah 1.** Tab Upload (drag-drop + `<input type="file" accept=".csv,.xlsx,.xls">` → `writeFile` → `load_table`; pemilih sheet bila `sheets.length > 1`), tab Ketik sendiri (pilih jumlah Y 1–3, X 0–10, baris; tabel `contenteditable`; paste dari Excel memecah `\t` dan `\n`; hasilnya disimpan sebagai CSV ke `/tmp/manual.csv` lalu `load_table`), tab Contoh (fetch `contoh/*.csv` → `writeFile` → `load_table`). Tampilkan pratinjau 10 baris dan `warnings` sebagai `.note.warn`, serta catatan privasi.
- [ ] **Step 2: Langkah 2.** Satu kartu per variabel: nama, peran Y/X, mode "satu kolom" atau "gabungan item" (chip kolom, klik = pilih, klik kanan atau tombol ↺ = unfavorable), combine sum/mean, skala opsional. Ada tombol tambah variabel X/Y (batas Y 3, X 10) dan pemilih kolom kelompok opsional. Setiap perubahan memanggil `prepare` (debounce 300 ms) lalu merender warning: `negative_item_total` dengan tombol "Balik skor {item}", `out_of_range` dengan input nilai pengganti + tombol "Perbaiki" (`set_cell` lalu `prepare`), `non_numeric`, dan jumlah baris yang dikeluarkan.
- [ ] **Step 3: Verifikasi di browser** dengan contoh kuesioner. Expected: terbaca 150 baris; setelah Y = P1–P10 dan X = S1–S10, muncul peringatan P7 dan S4 baris 87 = 55; tombol "Balik skor P7" membuat peringatan P7 hilang; memperbaiki S4 menjadi 5 membuat peringatan baris 87 hilang; info "3 baris dikeluarkan, 147 dianalisis". Upload `.xlsx` dua sheet memunculkan pemilih sheet. Paste 3×3 dari Excel ke tab Ketik sendiri mengisi tabel.
- [ ] **Step 4: Commit** — `git commit -m "feat: langkah input data dan atur variabel"`

---

### Task 11: Langkah 3–5 (tujuan, hasil, penyebab) dan grafik

**Files:**
- Create: `web/charts.js`
- Modify: `web/app.js`, `web/index.html`

**Interfaces:**
- Consumes: `call("check")`.
- Produces: `charts.js`: `histogram(el, values)`, `qq(el, qqData, onPick(row))`, `pp(el, ppData)`, `boxplot(el, values)`; `state.check` (hasil check).

- [ ] **Step 1: Langkah 3.** Enam kartu tujuan, dengan teks dari tabel langkah 3 di spec. Kartu dinonaktifkan dengan alasan bila syaratnya tidak terpenuhi (uji-t berpasangan butuh 2 Y; uji-t independen/ANOVA butuh kolom kelompok). Ada pilihan α 0,05/0,01 dan kalimat "Untuk regresi, yang harus normal adalah residual…". Tombol "Jalankan semua uji" → `check`; bila hasilnya error, tampilkan `showError`.
- [ ] **Step 2: Langkah 4.** Satu kartu status per target (warna + ikon ⛔/⚠️/✅/⏭ + teks "Tidak normal"/"Sedikit menyimpang, masih aman"/"Normal"/"Tidak bisa diuji") dengan `reason`, kartu "Kenapa kesimpulannya begini?" (`rejected` dari `total`), grafik histogram + kurva normal, Q-Q (titik dengan |z| > 2,5 berwarna merah dan bisa diklik → menampilkan baris), P-P, boxplot, serta `<details open>` tabel 7 uji (baris `ks_classic` selalu memuat peringatan "Terlalu longgar"). Penjelasan "(?)" maksimal 3 kalimat per istilah. Bila ada beberapa target, gunakan tab per target.
- [ ] **Step 3: Langkah 5.** Daftar `findings` per target (ikon sesuai severity) dengan tabel baris terkait (untuk regresi: Y, X, residual terstandar, Cook's D). Bila tidak ada temuan, tampilkan "Tidak ada penyebab yang menonjol." Nilai data tidak dihapus dari tampilan.
- [ ] **Step 4: Verifikasi di browser** dengan contoh kuesioner + regresi. Expected: kartu merah "Residual regresi: X1 → Y1"; tabel berisi 7 baris; temuan pertama efek plafon; klik titik merah di Q-Q menampilkan nomor barisnya. Dengan tujuan ANOVA dan kelompok JK, kartu ANOVA nonaktif dengan alasan "minimal 3 kelompok". Dengan contoh pretest–posttest + uji-t berpasangan, muncul target "Selisih Y2 − Y1".
- [ ] **Step 5: Commit** — `git commit -m "feat: langkah tujuan, hasil uji, dan penyebab"`

---

### Task 12: Langkah 6–7 (solusi dan laporan)

**Files:**
- Modify: `web/app.js`, `web/index.html`

**Interfaces:**
- Consumes: `call("remedy")`, `call("report")`, `call("set_cell")`.

- [ ] **Step 1: Langkah 6.** Kartu solusi berurutan dengan label sesuai spec: (1) perbaiki salah input/balik item, yang hanya muncul bila ada `data_error`/`unreversed_item` dan mengarahkan kembali ke langkah 2; (2) "Apakah kamu memang perlu normal?" dengan teks sesuai goal dan n; (3) uji alternatif: `remedy alternative`, tampilkan parametrik vs alternatif berdampingan + post-hoc Dunn, dan tombol "Pakai ini di laporan" yang menyimpan `state.chosenId`; (4) transformasi: pilih method, tampilkan before/after (status + histogram) dan catatan interpretasi; (5) eksklusi outlier dengan label "Hati-hati": checkbox per baris dari temuan `outliers` dan dropdown alasan wajib dari `REASONS`, tombol nonaktif sampai semua baris terpilih punya alasan, hasil before/after berdampingan. Tampilkan juga kalimat "Kami tidak menyediakan hapus otomatis sampai normal."
- [ ] **Step 2: Langkah 7.** `report` → paragraf (font serif seperti mockup), tabel hasil uji normalitas gaya APA (kolom: Uji, Statistik, n, p; dibuat dari `state.check`, berupa `<table>` biasa agar bisa disalin ke Word), tombol "Salin teks" (`navigator.clipboard`), "Unduh data hasil (CSV)" (Blob dari skor + transformasi, dibuat di browser), "Cetak / simpan PDF" (`window.print()` + `@media print` yang menyembunyikan header/stepper/tombol), dan daftar rujukan.
- [ ] **Step 3: Verifikasi di browser** dengan contoh kuesioner. Expected: bootstrap menampilkan CI yang tidak melewati 0; Yeo-Johnson menampilkan before/after; eksklusi tanpa alasan tidak bisa dijalankan; laporan memuat "W = …", perbaikan baris 87, "bootstrap", dan rujukan Kim (2013) serta Efron & Tibshirani (1993); hasil salin bisa ditempel di Word; pratinjau cetak tidak memuat tombol.
- [ ] **Step 4: Commit** — `git commit -m "feat: langkah solusi dan laporan"`

---

### Task 13: Uji privasi, mobile, review desain, dan publikasi

**Files:**
- Create: `README.md`, `.github/workflows/pages.yml`, `DESIGN.md` + `.impeccable/design.json` (ditulis oleh documenter), `.impeccable/review/desktop.png`, `.impeccable/review/mobile.png`

Step 5–8 dijalankan oleh controller, bukan subagent implementer, karena memanggil agent bawaan impeccable.

- [ ] **Step 1: Cek privasi.** Buka DevTools → Network, jalankan seluruh alur dengan file upload. Expected: request hanya ke `localhost`, `cdn.jsdelivr.net`, dan `fonts.googleapis.com`/`fonts.gstatic.com`; tidak ada request yang membawa isi data.
- [ ] **Step 2: Cek mobile.** Di lebar 375 px, jalani langkah 1–7. Expected: tidak ada scroll horizontal pada halaman, grafik menyesuaikan lebar, dan stepper bisa digeser.
- [ ] **Step 3: README.md** berisi: tujuan singkat, cara menjalankan lokal (`python -m http.server 8000 -d web`), cara menjalankan test (`pytest`), dan catatan bahwa semua data diproses di browser.
- [ ] **Step 4: GitHub Pages.** Workflow `pages.yml` memakai `actions/upload-pages-artifact` dengan `path: web` dan `actions/deploy-pages`. Push ke GitHub dan aktifkan Pages (dilakukan pemilik repo; minta izin dulu sebelum push).
- [ ] **Step 5: Detektor dan checklist.**
  - Jalankan `"C:/Users/Asus/.claude/plugins/cache/impeccable/impeccable/4.7.0/skills/impeccable/scripts/impeccable" detect --json web/index.html web/style.css web/app.js` sekali, lalu perbaiki temuan mekanis.
  - Lalui Pre-Delivery Checklist ui-ux-pro-max: tanpa emoji sebagai ikon, `cursor: pointer` di semua elemen yang bisa diklik, hover 150–300ms, kontras teks ≥ 4,5:1, fokus terlihat, `prefers-reduced-motion`, dan responsif di 375/768/1024/1440.
  - Lalui `consistency-checklist.md` dari skill brand terhadap `docs/brand-guidelines.md`.
- [ ] **Step 6: Tangkapan layar.** Alur dijalankan dengan contoh kuesioner sampai langkah 7. Entrance motion dimatikan, lalu tangkap `.impeccable/review/desktop.png` (lebar 1440, full page dari atas, langkah 4 Hasil) dan `.impeccable/review/mobile.png` (lebar 390). Buka kedua file dan pastikan isinya benar.
- [ ] **Step 7: Finish review impeccable.** Spawn `impeccable-finish-reviewer` (tanpa riwayat percakapan) dengan paket: permintaan asli, jawaban yang dikonfirmasi (nama Normalin, sapaan kamu, proyek pribadi, mockup disetujui), path artefak `web/index.html`, kedua screenshot, kontrak arah `.impeccable/surfaces/web-index-html.md`, temuan detektor, path craft-floor, dan `mockup/mockup.html` sebagai referensi kritik (build code-led, tanpa comp). Ikuti disposisinya (ship/fix/rebuild/recapture), dengan maksimal dua putaran perbaikan.
- [ ] **Step 8: Documenter.** Spawn `impeccable-documenter` dengan root proyek, artefak, kontrak arah, `PRODUCT.md`, dan batas tulis `DESIGN.md` + `.impeccable/design.json`. Pastikan keduanya ada dan memuat token.
- [ ] **Step 9: Commit** — `git add README.md .github DESIGN.md .impeccable && git commit -m "docs: README, DESIGN.md, dan deploy GitHub Pages"`
