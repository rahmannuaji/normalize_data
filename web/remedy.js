// Langkah 6–7: solusi berurutan (dengan label kejujuran) dan laporan siap tempel.
import { call } from "./engine.js?v=7";
import { histogram } from "./charts.js?v=7";
import { fmt, fmtP, trim, pill, STATUS } from "./results.js?v=7";

let state, go, showError, h, icon;

const REASONS = { salah_input: "Salah input", menjawab_asal: "Responden menjawab asal", di_luar_populasi: "Di luar populasi penelitian" };
const LABEL = { ok: ["circle-check", "Dianjurkan"], warn: ["triangle-alert", "Boleh dengan catatan"], bad: ["circle-x", "Hati-hati"] };
const METHODS = [["log", "Logaritma"], ["sqrt", "Akar kuadrat"], ["reciprocal", "Kebalikan"], ["boxcox", "Box-Cox"], ["yeojohnson", "Yeo-Johnson"], [null, "Tanpa transformasi"]];
const METHOD_NAME = { log: "logaritma natural", sqrt: "akar kuadrat", reciprocal: "kebalikan (1/x)", boxcox: "Box-Cox", yeojohnson: "Yeo-Johnson" };

const note = (kind, ic, ...kids) => h("div", { class: `note ${kind}` }, icon(ic), h("span", {}, ...kids));
const targetN = () => Math.min(...state.check.map((c) => c.n));
const findings = (...ids) => state.check.flatMap((c) => c.findings.filter((f) => ids.includes(f.id)).map((f) => ({ ...f, label: c.label })));

// Hasil solusi disimpan di state.remedy; dibuang bila hasil uji (state.check) sudah diganti.
function rem() {
  if (!state.remedy || state.remedy.for !== state.check) {
    state.remedy = { for: state.check, alt: null, tr: null, ex: null, sel: {}, method: null };
    state.chosenId = null;
  }
  return state.remedy;
}

// ---------- Kartu akordeon ----------
function card(rank, title, sub, kind, fill) {
  const [ic, text] = LABEL[kind];
  const body = h("div", { class: "body" });
  const hd = h("button", { type: "button", class: "hd", "aria-expanded": "false" },
    h("span", { class: "rank" }, String(rank)),
    h("span", { class: "grow" }, h("b", {}, title), h("span", { class: "small muted block" }, sub)),
    pill(kind, ic, text), icon("chevron-down"));
  const el = h("div", { class: "sol" }, hd, body);
  const c = { el, filled: false, open: false };
  c.fill = () => { c.filled = true; body.replaceChildren(); fill(body); };
  c.reset = () => { c.filled = false; body.replaceChildren(); if (c.open) c.fill(); };
  c.toggle = (on) => {
    c.open = on;
    el.classList.toggle("open", on);
    hd.setAttribute("aria-expanded", String(on));
    if (on && !c.filled) c.fill();
  };
  hd.addEventListener("click", () => c.toggle(!c.open));
  return c;
}

// ---------- Sebelum / sesudah ----------
function shapiroLine(c) {
  const t = c.tests.find((x) => x.id === "shapiro" && x.p != null);
  return t ? `Shapiro-Wilk W = ${fmt(t.stat, 3)}, p ${t.p < 0.001 ? fmtP(t.p) : "= " + fmtP(t.p)}` : (c.verdict.reason || "");
}
function side(title, c) {
  const [ic, text] = STATUS[c.verdict.status];
  const chart = h("div", { class: "chart-box", role: "img", "aria-label": `Histogram ${title.toLowerCase()}: ${c.label}` });
  const el = h("div", { class: "card" }, h("div", { class: "caption" }, title), h("div", {}, pill(c.verdict.status, ic, text)),
    h("p", { class: "small" }, `n = ${c.n} · ${shapiroLine(c)}`), c.verdict.status === "skipped" ? null : chart);
  return { el, draw: () => c.verdict.status !== "skipped" && histogram(chart, c.plot.values) };
}
function compare(before, after) {
  const out = h("div", {});
  const draws = [];
  before.forEach((b, i) => {
    const l = side("Sebelum", b);
    const r = side("Sesudah", after[i]);
    draws.push(l.draw, r.draw);
    out.append(h("h3", { class: "target" }, b.label), h("div", { class: "grid g2" }, l.el, r.el));
  });
  return { el: out, draw: () => draws.forEach((d) => d()) };
}
function showCompare(box, res) {
  const c = compare(res.before, res.after);
  box.append(c.el);
  c.draw();
}

// ---------- Kartu 1: salah input / item belum dibalik ----------
function fillFix(body) {
  const fs = findings("data_error", "unreversed_item");
  const seen = new Set();
  body.append(h("p", {}, "Ini bukan manipulasi, karena kamu memperbaiki kesalahan. Cek ke kuesioner asli dulu, lalu jalankan ulang pengujian."),
    h("ul", { class: "small" }, fs.filter((f) => !seen.has(f.title) && seen.add(f.title)).map((f) => h("li", {}, f.title))),
    h("button", { type: "button", class: "btn small primary", "data-go": "2" }, "Perbaiki di langkah 2", icon("arrow-right")));
}

// ---------- Kartu 2: apakah perlu normal? ----------
function needText() {
  const goal = state.checkGoal;
  const n = targetN();
  const big = n >= 30;
  if (goal === "normality_only") return "Kalau tujuanmu hanya melaporkan normalitas, tidak ada yang perlu \"diperbaiki\". Laporkan hasilnya apa adanya dan jelaskan penyebabnya.";
  if (goal === "regression") return n >= 100
    ? `Dengan n = ${n}, uji-t koefisien regresi biasanya tetap cukup akurat walaupun residual tidak normal (teorema limit pusat). Tetap laporkan hasil ujinya, dan perkuat dengan solusi 3 (bootstrap atau galat baku robust).`
    : `Dengan n = ${n}, jumlah data relatif kecil sehingga residual yang tidak normal bisa memengaruhi uji-t dan interval kepercayaan. Sebaiknya perkuat dengan solusi 3 (bootstrap atau galat baku robust).`;
  if (goal === "correlation") return n >= 100
    ? `Dengan n = ${n}, Pearson relatif tahan terhadap penyimpangan sedang. Tapi pencilan tetap bisa menggeser r, jadi bandingkan dengan Spearman (solusi 3).`
    : `Dengan n = ${n}, Pearson sensitif terhadap kemiringan dan pencilan. Bandingkan dengan Spearman atau Kendall (solusi 3).`;
  if (goal === "ttest_paired") return big
    ? `Yang perlu normal adalah selisih sebelum dan sesudah. Dengan n = ${n} (≥ 30), uji-t berpasangan cukup tahan terhadap penyimpangan sedang. Tetap laporkan, dan perkuat dengan Wilcoxon (solusi 3).`
    : `Yang perlu normal adalah selisih sebelum dan sesudah. Dengan n = ${n}, penyimpangan lebih berisiko, jadi pakai Wilcoxon (solusi 3).`;
  return big
    ? `Uji-t dan ANOVA cukup tahan terhadap penyimpangan sedang bila tiap kelompok berisi ≥ 30 responden (terkecil sekarang n = ${n}). Tetap laporkan, dan perkuat dengan solusi 3.`
    : `Salah satu kelompok hanya berisi n = ${n}, jadi penyimpangan lebih berisiko. Pakai uji alternatif (solusi 3).`;
}
const fillNeed = (body) => body.append(h("p", {}, needText()), h("p", { class: "caption" }, "Rujukan: Kim (2013); Ghasemi & Zahediasl (2012). Lihat daftar di langkah 7."));

// ---------- Kartu 3: uji alternatif ----------
// Simbol dan df dari engine (stat_name, df), sama dengan kalimat laporan: t(df), F(df1, df2), U, W, H(df), r, ρ, τ, B.
const dfText = (df) => (df == null ? "" : `(${[].concat(df).map((d) => (Number.isInteger(d) ? String(d) : fmt(d, 2))).join(", ")})`);
function statText(r) {
  if (r.stat_name === "B") return `B = ${fmt(r.stat, 3)}` + (r.t != null ? `; t${dfText(r.df)} = ${fmt(r.t, 2)}` : "");
  const v = ["U", "W"].includes(r.stat_name) ? (Number.isInteger(r.stat) ? String(r.stat) : fmt(r.stat, 1)) : fmt(r.stat, 2);
  return `${r.stat_name}${dfText(r.df)} = ${v}`;
}
function resultCard(r, canPick, many) {
  const picked = state.chosenId === r.id;
  const lines = [];
  const d = r.stat_name === "B" ? 3 : 2;
  if (r.stat != null) lines.push(h("div", {}, h("b", {}, statText(r)), r.p != null ? `, p ${r.p < 0.001 ? fmtP(r.p) : "= " + fmtP(r.p)}` : ""));
  if (r.ci) {
    const cross = r.ci[0] <= 0 && r.ci[1] >= 0;
    lines.push(h("div", { class: "small" }, `CI 95% [${fmt(r.ci[0], d)}; ${fmt(r.ci[1], d)}]`),
      h("div", { class: `small ${cross ? "" : "yes"}` }, icon(cross ? "circle-slash" : "circle-check"), cross ? "melewati 0" : "tidak melewati 0"));
  }
  if (r.effect != null && r.effect !== r.stat) lines.push(h("div", { class: "caption" }, `${r.effect_name}: ${fmt(r.effect, 2)}`));
  const btn = canPick ? h("button", { type: "button", class: `btn small${picked ? "" : " primary"}`, "aria-pressed": String(picked), onclick: () => { state.chosenId = picked ? null : r.id; renderAlt(); } },
    picked ? [icon("circle-check"), "Dipakai di laporan"] : "Pakai ini di laporan") : null;
  const all = canPick && many ? h("div", { class: "caption" }, "Berlaku untuk semua pasangan variabel.") : null;
  return h("div", { class: `card${picked ? " picked" : ""}` }, h("div", { class: "caption" }, r.name), r.recommended ? h("div", {}, pill("ok", "circle-check", "Dianjurkan")) : null, ...lines, btn, all);
}

let altBox;
function renderAlt() {
  const { alt } = rem();
  const out = [];
  const labels = [...new Set([...alt.parametric, ...alt.alternatives].map((r) => r.label))];
  const seen = new Set();
  labels.forEach((l) => {
    if (labels.length > 1) out.push(h("h3", { class: "target" }, l));
    const par = alt.parametric.filter((r) => r.label === l);
    const alts = alt.alternatives.filter((r) => r.label === l);
    out.push(h("div", { class: "compare" }, par.map((r) => resultCard(r, false, false)), alts.map((r) => { const first = !seen.has(r.id); seen.add(r.id); return resultCard(r, first, labels.length > 1); })));
  });
  if (alt.posthoc?.length) {
    const a = state.checkAlpha;
    out.push(h("h3", { class: "target" }, "Uji lanjut Dunn (koreksi Bonferroni)"),
      h("div", { class: "tablewrap", tabindex: "0", role: "region", "aria-label": "Uji lanjut Dunn" }, h("table", {},
        h("thead", {}, h("tr", {}, ["Pasangan", "z", "p", "p disesuaikan", "Hasil"].map((t) => h("th", {}, t)))),
        h("tbody", {}, alt.posthoc.map((r) => h("tr", {}, h("td", {}, r.label), h("td", {}, fmt(r.z, 2)), h("td", {}, fmtP(r.p)), h("td", {}, fmtP(r.p_adj)),
          h("td", {}, r.p_adj < a ? [icon("circle-check"), " Berbeda nyata"] : [icon("circle-slash"), " Tidak berbeda nyata"])))))));
  }
  if (state.chosenId) out.push(note("ok", "circle-check", `Laporan akan memakai ${alt.alternatives.find((r) => r.id === state.chosenId)?.name}. Transformasi data tidak ikut dilaporkan karena alternatif dijalankan pada data aslinya.`));
  else out.push(note("info", "info", "Pilih satu hasil dengan tombol \"Pakai ini di laporan\" bila kamu ingin laporannya memuat hasil itu."));
  altBox.replaceChildren(...out);
}

async function fillAlt(body) {
  altBox = h("div", { "aria-live": "polite" });
  body.append(altBox);
  if (state.checkGoal === "normality_only") return altBox.append(note("info", "info", "Tujuan \"cek normalitas saja\" tidak punya uji alternatif."));
  const R = rem();
  if (R.alt) return renderAlt();
  altBox.append(note("info", "info", "Menghitung (bootstrap 5.000 sampel ulang bisa memakan beberapa detik)…"));
  try {
    R.alt = await call("remedy", { kind: "alternative" });
    if (rem() !== R) return; // hasil uji sudah diganti selagi menghitung (halaman tetap bisa dipakai)
    renderAlt();
  } catch (err) {
    altBox.replaceChildren();
    showError(err.message);
  }
}

// ---------- Kartu 4: transformasi ----------
function infoLine(name, i) {
  let t = `${name}: ${METHOD_NAME[i.method]}`;
  if (i.lambda != null) t += ` (λ = ${fmt(i.lambda, 2)})`;
  if (i.reflected) t += ", dicerminkan dulu";
  if (i.shift) t += `, digeser ${fmt(i.shift, 2)}`;
  return t;
}
function fillTransform(body) {
  const R = rem();
  const out = h("div", { "aria-live": "polite" });
  const btns = METHODS.map(([m, label]) => h("button", { type: "button", "aria-pressed": String(R.method === m), class: R.method === m ? "on" : "", onclick: () => run(m) }, label));
  body.append(h("p", { class: "small" }, "Pilih satu metode. Hasilnya langsung diuji ulang dan ditampilkan berdampingan."), h("div", { class: "tabs", role: "group", "aria-label": "Metode transformasi" }, btns), out);
  function show() {
    btns.forEach((b, i) => { const on = METHODS[i][0] === R.method; b.classList.toggle("on", on); b.setAttribute("aria-pressed", String(on)); });
    out.replaceChildren();
    if (!R.tr) {
      if (R.method) out.append(note("warn", "triangle-alert", `Transformasi ${METHOD_NAME[R.method]} masih aktif, tapi datanya berubah setelah pengeluaran baris. Pilih metode lagi untuk melihat sebelum dan sesudahnya.`));
      return;
    }
    const info = R.tr.info;
    if (!info) return out.append(note("info", "info", "Transformasi dibatalkan. Analisis memakai skor aslimu."));
    const list = Object.entries(info).map(([n, i]) => infoLine(n, i));
    out.append(h("ul", { class: "small" }, list.map((t) => h("li", {}, t))));
    showCompare(out, R.tr);
    out.append(note("warn", "triangle-alert", h("b", {}, "Catatan interpretasi: "), "yang kamu analisis jadi skor hasil transformasi, sehingga koefisien dan rata-rata tidak lagi dalam satuan skor aslimu."
      + (Object.values(info).some((i) => i.reflected) ? " Data miring ke kiri dicerminkan dulu, jadi arah skornya terbalik (skor tinggi menjadi rendah)." : "")));
  }
  async function run(m) {
    try {
      if (R.method) await call("remedy", { kind: "transform", method: null }); // supaya "sebelum" selalu data tanpa transformasi
      R.method = null;
      R.tr = await call("remedy", { kind: "transform", method: m });
      R.method = m;
      show();
    } catch (err) {
      showError(err.message);
    }
  }
  show();
}

// ---------- Kartu 5: eksklusi outlier ----------
function fillExclude(body) {
  const R = rem();
  const out = h("div", { "aria-live": "polite" });
  const cand = new Map();
  findings("outliers").forEach((f) => (f.table?.rows || f.rows.map((r) => [r])).forEach((r) => {
    if (!cand.has(r[0])) cand.set(r[0], { label: f.label, detail: (f.table?.columns || []).slice(1).map((c, i) => `${c} ${trim(r[i + 1])}`).join(" · ") });
  }));
  body.append(note("bad", "ban", h("b", {}, "Kami tidak menyediakan hapus otomatis sampai normal."), " Itu termasuk manipulasi data. Kamu boleh mengeluarkan baris hanya bila ada alasan yang jelas, dan alasannya dicatat di laporan."));
  if (!cand.size) return body.append(note("info", "info", "Tidak ada baris yang ditandai sebagai pencilan di langkah 5."), out);
  const apply = h("button", { type: "button", class: "btn primary", onclick: () => run(true) }, "Jalankan tanpa baris terpilih");
  const clear = h("button", { type: "button", class: "btn", hidden: !R.ex, onclick: () => run(false) }, "Batalkan pengeluaran");
  const sync = () => {
    const rows = Object.keys(R.sel);
    apply.disabled = !rows.length || rows.some((r) => !R.sel[r]);
    apply.title = apply.disabled ? "Pilih minimal satu baris dan beri alasan untuk tiap baris yang dipilih." : "";
  };
  const list = [...cand].map(([row, c]) => {
    const key = String(row);
    const sel = h("select", { class: "inp", "aria-label": `Alasan mengeluarkan baris ${row}` }, h("option", { value: "" }, "Pilih alasan…"), Object.entries(REASONS).map(([k, v]) => h("option", { value: k }, v)));
    sel.disabled = !(key in R.sel);
    sel.value = R.sel[key] || "";
    const cb = h("input", { type: "checkbox" });
    cb.checked = key in R.sel;
    cb.addEventListener("change", () => { if (cb.checked) R.sel[key] = sel.value; else delete R.sel[key]; sel.disabled = !cb.checked; sync(); });
    sel.addEventListener("change", () => { R.sel[key] = sel.value; sync(); });
    return h("div", { class: "xrow" }, h("label", {}, cb, h("span", {}, h("b", {}, `Baris ${row}`), h("span", { class: "caption block" }, `${c.label}${c.detail ? " · " + c.detail : ""}`))), sel);
  });
  body.append(h("div", { class: "xlist" }, list), h("div", { class: "actions", style: "margin-top:var(--space-md)" }, apply, clear), out);
  sync();
  function show() {
    out.replaceChildren();
    if (R.ex) {
      out.append(note("info", "info", `${Object.keys(R.ex).length} baris dikeluarkan: ${Object.entries(R.ex).map(([r, k]) => `baris ${r} (${REASONS[k]})`).join("; ")}.`));
      if (R.method) out.append(note("info", "info", "Transformasi yang kamu pilih di solusi 4 ikut dipakai pada perbandingan ini."));
      if (R.resetChosen) out.append(note("warn", "triangle-alert", "Hasil uji alternatif lama dibuang karena datanya berubah. Buka solusi 3 dan pilih lagi bila perlu."));
      showCompare(out, R.exRes);
    }
    clear.hidden = !R.ex;
  }
  async function run(on) {
    try {
      const reasons = on ? { ...R.sel } : {};
      const res = await call("remedy", { kind: "exclude", reasons });
      R.ex = on ? reasons : null;
      R.exRes = res;
      R.resetChosen = !!state.chosenId;
      if (!on) R.sel = {};
      R.tr = null; // sebelum/sesudah transformasi lama dihitung dari data sebelum pengeluaran
      trc.reset();
      R.alt = null; // mesin membuang hasil alternatif lama
      state.chosenId = null;
      alt.reset();
      if (!on) { exc.reset(); return; }
      show();
    } catch (err) {
      showError(err.message);
    }
  }
  show();
}

// ---------- Langkah 6 ----------
let alt, exc, trc, root6, root7;

function renderSolutions() {
  if (!state.check) return void root6.replaceChildren(note("info", "info", "Belum ada hasil. Jalankan semua uji di langkah 3 dulu."));
  rem();
  const allOk = state.check.every((c) => c.verdict.status === "ok");
  const cards = [];
  if (findings("data_error", "unreversed_item").length) cards.push(card(0, "Perbaiki salah input dan item yang belum dibalik", "Kembali ke langkah 2", "ok", fillFix));
  cards.push(card(0, "Apakah kamu memang perlu normal?", `n = ${targetN()}`, "ok", fillNeed));
  alt = card(0, "Pakai metode yang tidak butuh normalitas", "Uji alternatif dan bootstrap", "ok", fillAlt);
  trc = card(0, "Transformasi data", "Log, akar kuadrat, kebalikan, Box-Cox, Yeo-Johnson", "warn", fillTransform);
  cards.push(alt, trc);
  exc = card(0, "Mengeluarkan pencilan", "Hanya dengan alasan yang jelas", "bad", fillExclude);
  cards.push(exc);
  cards.forEach((c, i) => c.el.querySelector(".rank").textContent = String(i + 1));
  root6.replaceChildren(allOk ? note("ok", "circle-check", "Semua yang diuji sudah normal, jadi kamu tidak wajib memperbaiki apa pun. Pilihan di bawah tetap bisa dicoba.") : "", ...cards.map((c) => c.el));
  cards[0].toggle(true);
}

// ---------- Langkah 7 ----------
function apaTables() {
  return state.check.map((c, i) => {
    const rows = c.tests.map((t) => {
      const sk = t.id === "skew_kurt" && c.moments;
      const stat = sk ? `${fmt(c.moments.skew)}; ${fmt(c.moments.kurt)}` : t.skipped_reason || t.stat == null ? "–" : fmt(t.stat, 3);
      return h("tr", {}, h("td", {}, t.name), h("td", {}, stat), h("td", {}, String(c.n)), h("td", {}, sk || t.skipped_reason || t.p == null ? "–" : fmtP(t.p)));
    });
    return h("div", { class: "apa-box" }, h("table", { class: "apa" }, h("caption", {}, `Tabel ${i + 1}. Hasil uji normalitas ${c.subject || c.label}`),
      h("thead", {}, h("tr", {}, ["Uji", "Statistik", "n", "p"].map((t) => h("th", {}, t)))), h("tbody", {}, rows)),
      h("p", { class: "caption" }, `Catatan. Taraf signifikansi α = ${fmt(state.checkAlpha)}.`));
  });
}

const quote = (v) => (/[;"\n\r]/.test(v) ? `"${v.replaceAll('"', '""')}"` : v);
// Teks yang diawali = + - @ tab atau CR diberi awalan ' supaya Excel tidak menjalankannya sebagai rumus.
const csvCell = (v) => (v == null ? "" : typeof v === "number" ? String(v).replace(".", ",") : quote(/^[=+\-@\t\r]/.test(v) ? "'" + v : v));
async function downloadCsv() {
  try {
    const d = await call("export_scores", { transformed: !state.chosenId });
    const head = d.columns.map((c) => (c === "__group" ? "Kelompok" : c));
    const text = [head, ...d.rows].map((r) => r.map(csvCell).join(";")).join("\r\n");
    const url = URL.createObjectURL(new Blob([String.fromCharCode(0xfeff) + text], { type: "text/csv;charset=utf-8" })); // BOM + titik koma + koma desimal: terbuka rapi di Excel Indonesia
    const a = h("a", { href: url, download: "normalin-data-hasil.csv" });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (err) {
    showError(err.message);
  }
}

// Cadangan bila Clipboard API ditolak (mis. halaman tidak sedang fokus).
function legacyCopy(text) {
  const ta = h("textarea", { "aria-hidden": "true", tabindex: "-1", style: "position:fixed;opacity:0" });
  ta.value = text;
  document.body.append(ta);
  ta.select();
  const ok = document.execCommand("copy");
  ta.remove();
  return ok;
}

async function renderReport() {
  if (!state.check) return void root7.replaceChildren(note("info", "info", "Belum ada hasil. Jalankan semua uji di langkah 3 dulu."));
  root7.replaceChildren(note("info", "info", "Menyusun laporan…"));
  let rep;
  try {
    rem();
    rep = await call("report", { chosen_id: state.chosenId || null });
  } catch (err) {
    root7.replaceChildren();
    return showError(err.message);
  }
  const text = h("div", { class: "report", id: "reportText" }, rep.text.split(/\n\s*\n/).map((p) => h("p", {}, p)));
  const copyLabel = h("span", {}, "Salin teks");
  const copyBtn = h("button", { type: "button", class: "btn primary", onclick: async () => {
    try {
      try {
        await navigator.clipboard.writeText(rep.text);
      } catch {
        if (!legacyCopy(rep.text)) throw new Error("copy");
      }
      copyLabel.textContent = "Tersalin";
      setTimeout(() => (copyLabel.textContent = "Salin teks"), 2000);
    } catch {
      getSelection().selectAllChildren(text);
      text.scrollIntoView({ block: "nearest" });
      showError("Browser tidak mengizinkan menyalin otomatis. Teks laporan sudah kami blok, tekan Ctrl+C (Cmd+C di Mac).");
    }
  } }, icon("copy"), copyLabel);
  root7.replaceChildren(
    text,
    h("div", { class: "actions", style: "margin-top:var(--space-md)", "aria-live": "polite" }, copyBtn,
      h("button", { type: "button", class: "btn", onclick: downloadCsv }, icon("download"), "Unduh data hasil (CSV)"),
      h("button", { type: "button", class: "btn", onclick: () => window.print() }, icon("printer"), "Cetak / simpan PDF")),
    h("h3", { style: "margin-top:var(--space-xl)" }, "Tabel hasil uji normalitas"), ...apaTables(),
    h("h3", { style: "margin-top:var(--space-lg)" }, "Rujukan untuk keputusanmu"), ...rep.references.map((r) => h("p", { class: "ref" }, r)));
}

export function initRemedy(deps) {
  ({ state, go, showError, h, icon } = deps);
  root6 = document.getElementById("step6");
  root7 = document.getElementById("step7");
  document.addEventListener("step", (e) => {
    if (e.detail === 6) renderSolutions();
    else if (e.detail === 7) renderReport();
  });
}
