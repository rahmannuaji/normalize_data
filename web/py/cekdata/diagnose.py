import numpy as np

_ORDER = {"high": 0, "medium": 1, "low": 2}


def _f(v, d=2):
    return f"{v:.{d}f}".replace(".", ",").replace("-", "−")


def _rows(target, mask):
    return [r for r, k in zip(target["rows"], mask) if k]


def diagnose(target, m, score_range, y_values, prep_warnings):
    x = np.asarray(target["values"], dtype=float)
    n = len(x)
    out = []

    def add(id_, sev, title, detail, rows=()):
        out.append({"id": id_, "severity": sev, "title": title, "detail": detail, "rows": list(rows)})

    oor = [w for w in prep_warnings if w["kind"] == "out_of_range"]
    if oor:
        add("data_error", "high", f"{len(oor)} skor di luar rentang jawaban",
            "Ada skor yang tidak mungkin muncul dari skala kuesionernya, kemungkinan salah ketik: "
            + "; ".join(f"baris {w['row']} kolom {w['column']} bernilai {_f(w['value'], 0) if float(w['value']).is_integer() else _f(w['value'])}" for w in oor)
            + ". Periksa dulu ke lembar jawaban aslinya.", [w["row"] for w in oor])
    for w in (w for w in prep_warnings if w["kind"] == "negative_item_total"):
        add("unreversed_item", "high", f"Butir {w['item']} berlawanan arah dengan total {w['variable']}",
            f"Korelasi butir {w['item']} dengan total butir lain {w['variable']} bernilai {_f(w['r'])}. "
            "Kalau butir ini pernyataan negatif, cek apakah skornya sudah dibalik.")

    if score_range is not None and y_values is not None and len(y_values):
        y = np.asarray(y_values, dtype=float)
        lo, hi = score_range
        span = hi - lo
        for id_, mask, name, near in (("ceiling", y >= hi - 0.1 * span, "Efek plafon", "maksimal"),
                                      ("floor", y <= lo + 0.1 * span, "Efek lantai", "minimal")):
            pct = 100 * mask.mean()
            if pct >= 15:
                add(id_, "high", f"{name}: {_f(pct, 0)}% responden memberi skor hampir {near}",
                    f"{int(mask.sum())} dari {len(y)} skor berada di ujung {'atas' if id_ == 'ceiling' else 'bawah'} "
                    f"rentang ({_f(lo, 0)}–{_f(hi, 0)}), sehingga sebaran terpotong dan sulit simetris.", _rows(target, mask))

    sk, ku = m.get("skew"), m.get("kurt")
    if sk is not None:
        if abs(sk) >= 0.5:
            left = sk < 0
            add("skew_left" if left else "skew_right", "high" if abs(sk) >= 1 else "medium",
                f"Sebaran miring ke {'kiri' if left else 'kanan'} (skewness {_f(sk)})",
                "Sebagian besar nilai menumpuk di sisi " + ("tinggi" if left else "rendah")
                + ", dengan ekor panjang ke sisi " + ("rendah." if left else "tinggi."))
        if ku >= 1:
            add("heavy_tails", "medium", f"Ekor sebaran terlalu tebal (kurtosis {_f(ku)})",
                "Ada lebih banyak nilai ekstrem daripada yang lazim pada sebaran normal.")
        elif ku <= -1:
            add("light_tails", "medium", f"Sebaran terlalu datar (kurtosis {_f(ku)})",
                "Nilai menyebar rata dan hampir tanpa nilai ekstrem, lebih datar daripada lonceng normal.")

    mask = np.zeros(n, bool)
    if n >= 4:
        q1, q3 = np.percentile(x, [25, 75])
        mask |= (x < q1 - 1.5 * (q3 - q1)) | (x > q3 + 1.5 * (q3 - q1))
        sd = x.std(ddof=1)
        if sd > 0:
            mask |= np.abs((x - x.mean()) / sd) > 3
    mod = target.get("model")
    if mod:
        mask |= np.abs(np.asarray(mod["std_resid"])) > 3
        mask |= np.asarray(mod["cooks"]) > 4 / n
        if mod.get("mahal_p") is not None:
            mask |= np.asarray(mod["mahal_p"]) < 0.001
    if mask.any():
        add("outliers", "medium", f"{int(mask.sum())} data pencilan",
            "Nilai pada baris ini jauh dari kebanyakan data lainnya. Periksa apakah salah input atau memang responden yang unik.",
            _rows(target, mask))

    if sk is not None and n > 3:
        bc = (sk ** 2 + 1) / (ku + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3)))
        if bc > 0.555:
            add("bimodal", "medium", f"Sebaran kemungkinan punya dua puncak (koefisien {_f(bc, 3)})",
                "Koefisien bimodalitas di atas 0,555. Bisa jadi ada dua kelompok responden yang tercampur.")

    nu = len(np.unique(x))
    if nu <= 5:
        add("low_variety", "low", f"Hanya {nu} nilai berbeda",
            "Variasi nilai sangat sedikit, jadi uji normalitas kurang bermakna.")

    return sorted(out, key=lambda d: _ORDER[d["severity"]])
