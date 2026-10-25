"""Bangkitkan dataset contoh (seed 2026). Jalankan: python tools/make_examples.py"""
import pathlib
import numpy as np
import pandas as pd

CEIL = 4.2  # konstanta efek plafon item Y; naikkan bila status target tidak "bad"
OUT = pathlib.Path(__file__).resolve().parent.parent / "web" / "contoh"


def item(rng, base, slope, lat):
    return np.clip(np.round(base + slope * lat + rng.normal(0, 0.6, len(lat))), 1, 5).astype(int)


def kuesioner(rng, n=150):
    lx = rng.normal(size=n)
    ly = 0.5 * lx + rng.normal(0, 0.85, n)
    d = {"No": np.arange(1, n + 1)}
    for i in range(1, 11):
        d[f"P{i}"] = item(rng, CEIL, 0.8, ly)
    d["P7"] = 6 - d["P7"]
    for i in range(1, 11):
        d[f"S{i}"] = item(rng, 3.4, 0.9, lx)
    d["S4"][86] = 55
    d["JK"] = np.where(np.arange(n) % 2 == 0, "L", "P")
    df = pd.DataFrame(d)
    df["P2"] = df["P2"].astype("Int64")
    df.loc[[19, 44, 100], "P2"] = pd.NA
    return df


def pretest_posttest(rng, n=40):
    pre = rng.normal(60, 10, n)
    post = pre + rng.gamma(2, 3, n)
    return pd.DataFrame({"No": np.arange(1, n + 1), "Pre": np.round(pre).astype(int), "Post": np.round(post).astype(int)})


if __name__ == "__main__":
    rng = np.random.default_rng(2026)
    for name, df in (("kuesioner_psikologi", kuesioner(rng)), ("pretest_posttest", pretest_posttest(rng))):
        df.to_csv(OUT / f"{name}.csv", sep=";", decimal=",", index=False, encoding="utf-8-sig")
