// Langkah 3–5: pilih tujuan analisis, hasil uji normalitas (dengan grafik), dan penyebab ketidaknormalan.
import { call } from "./engine.js";
import { histogram, qq, pp, boxplot, Z_FLAG } from "./charts.js";

let state, go, showError, h, icon;

const GOALS = [
  ["correlation", "Hubungan dua variabel", "Korelasi Pearson · yang dicek: tiap variabel", "link"],
  ["regression", "Pengaruh X terhadap Y", "Regresi linear · yang dicek: residual", "trending-up"],
  ["ttest_ind", "Bandingkan 2 kelompok", "Uji-t independen · yang dicek: tiap kelompok", "scale"],
  ["ttest_paired", "Sebelum vs sesudah", "Uji-t berpasangan · yang dicek: selisihnya", "repeat"],
  ["anova", "Bandingkan lebih dari 2 kelompok", "ANOVA satu arah · yang dicek: residual", "puzzle"],
  ["normality_only", "Cuma mau cek normalitas", "Tiap variabel yang dipilih", "search"],
];
const GOAL_NAME = { correlation: "Korelasi", regression: "Regresi", ttest_ind: "Uji-t independen", ttest_paired: "Uji-t berpasangan", anova: "ANOVA satu arah", normality_only: "Cek normalitas" };

const STATUS = {
  bad: ["circle-x", "Tidak normal"],
  warn: ["triangle-alert", "Sedikit menyimpang, masih aman"],
  ok: ["circle-check", "Normal"],
  skipped: ["circle-slash", "Tidak bisa diuji"],
};

const TEST_INFO = {
  shapiro: "Paling dianjurkan untuk n kecil sampai menengah.",
  lilliefors: "Versi KS yang benar bila mean dan SD dihitung dari datamu.",
  ks_classic: "Mirip \"One-Sample K-S\" di SPSS. Sering dipakai di skripsi.",
  anderson: "Lebih peka terhadap ekor distribusi.",
  jarque_bera: "Berdasarkan skewness dan kurtosis, cocok untuk n besar.",
  dagostino: "Gabungan skewness dan kurtosis.",
  skew_kurt: "Ukuran besarnya penyimpangan, bukan sekadar signifikan atau tidak.",
};

const HELP = {
  hist: "Batang menunjukkan berapa responden di tiap rentang nilai. Garis hitam adalah bentuk lonceng normal yang ideal. Makin mirip batang dengan garis, makin normal.",
  qq: "Kalau data normal, titik mengikuti garis lurus. Titik merah adalah responden yang paling menyimpang (lebih dari 2,5 simpangan baku). Klik titik merah untuk melihat nomor barisnya.",
  pp: "Sama seperti Q-Q tetapi membandingkan proporsi kumulatif. Titik yang rapat di garis berarti data mendekati normal. Grafik ini yang sering diminta dosen untuk regresi.",
  box: "Kotak berisi separuh data di tengah, garis di dalam kotak adalah median. Titik merah di luar kumis adalah pencilan. Kotak yang tidak simetris menandakan data miring.",
};

const RULE = {
  "n<50": "Jumlah data kurang dari 50, jadi Shapiro-Wilk jadi penentu utama.",
  "50-300": "Jumlah data antara 50 dan 300, jadi dipakai Shapiro-Wilk ditambah z-skewness dan z-kurtosis (batas |z| < 3,29; Kim, 2013).",
  ">300": "Jumlah data di atas 300. Uji formal hampir selalu menolak penyimpangan kecil, jadi dipakai nilai skewness (< 2) dan kurtosis (< 7) serta grafik (Kim, 2013; West dkk., 1995).",
};

// ---------- Format angka (koma desimal, minus ber-tanda −) ----------
const fmt = (v, d = 2) => (v == null ? "–" : v.toFixed(d).replace(".", ",").replace("-", "−"));
const fmtP = (p) => (p < 0.001 ? "< 0,001" : fmt(p, 3));
const trim = (v) => (typeof v === "number" ? String(Math.round(v * 1000) / 1000).replace(".", ",").replace("-", "−") : v == null ? "–" : String(v));
const MAX_ROWS = 30;

function pill(kind, ic, text) {
  return h("span", { class: `pill ${kind}` }, icon(ic), text);
}

// Judul kartu dengan tombol (?) yang membuka penjelasan singkat.
function titleWithHelp(text, help) {
  const tip = h("p", { class: "caption help", hidden: true }, help);
  const btn = h("button", { type: "button", class: "q", "aria-expanded": "false", "aria-label": `Penjelasan: ${text}`, onclick: () => { tip.hidden = !tip.hidden; btn.setAttribute("aria-expanded", String(!tip.hidden)); } }, icon("circle-help"));
  return [h("h3", {}, text, btn), tip];
}

// ---------- Langkah 3 ----------
function goalAvailability() {
  const vars = state.variables.filter((v) => v.columns.length);
  const nY = vars.filter((v) => v.role === "Y").length;
  const nX = vars.filter((v) => v.role === "X").length;
  const groups = state.prep?.groups ? Object.keys(state.prep.groups).length : 0;
  const gname = state.group || "";
  const noGroup = "Butuh kolom kelompok. Pilih di langkah 2.";
  const none = !state.prep ? "Atur variabel dulu di langkah 2." : null;
  return {
    correlation: none || (vars.length < 2 ? "Butuh minimal 2 variabel." : null),
    regression: none || (!nY || !nX ? "Butuh minimal satu variabel Y dan satu X." : null),
    ttest_ind: none || (!groups ? noGroup : groups !== 2 ? `Butuh tepat 2 kelompok (kolom ${gname} punya ${groups}).` : null),
    ttest_paired: none || (nY < 2 ? "Butuh 2 variabel Y: sebelum dan sesudah." : null),
    anova: none || (!groups ? noGroup : groups < 3 ? `Butuh minimal 3 kelompok (kolom ${gname} punya ${groups}).` : null),
    normality_only: none || (!vars.length ? "Butuh minimal satu variabel." : null),
  };
}

function renderGoals() {
  const why = goalAvailability();
  if (!state.goal || why[state.goal]) state.goal = !why.regression ? "regression" : (GOALS.find(([id]) => !why[id])?.[0] ?? null);
  state.alpha ??= 0.05;
  const cards = GOALS.map(([id, title, desc, ic]) => {
    const off = why[id];
    return h("button", {
      type: "button", role: "radio", class: `opt${state.goal === id ? " on" : ""}`, "aria-checked": String(state.goal === id), disabled: !!off,
      onclick: () => { state.goal = id; renderGoals(); },
    }, icon(ic), h("b", {}, title), h("small", {}, desc), off ? h("small", { class: "why" }, icon("ban"), off) : null);
  });
  const alphaBtns = [0.05, 0.01].map((a) => h("button", { type: "button", class: state.alpha === a ? "on" : "", "aria-pressed": String(state.alpha === a), onclick: () => { state.alpha = a; renderGoals(); } }, fmt(a)));
  root3.replaceChildren(
    h("div", { class: "grid g3", role: "radiogroup", "aria-label": "Tujuan analisis" }, cards),
    h("div", { class: "note info" }, icon("info"), h("span", {}, h("b", {}, "Untuk regresi, yang harus normal adalah residual, bukan data mentahnya."), " Banyak skripsi dan paper keliru di sini.")),
    h("div", { class: "field alpha" }, h("span", {}, "Taraf signifikansi (α)"), h("div", { class: "tabs", role: "group", "aria-label": "Taraf signifikansi" }, alphaBtns)),
  );
  next3.disabled = !state.goal;
}

async function runCheck() {
  next3.disabled = true;
  const label = next3.firstChild;
  const old = label.textContent;
  label.textContent = "Menjalankan uji…";
  try {
    const res = await call("check", { goal: state.goal, alpha: state.alpha });
    state.check = res.targets;
    state.checkGoal = state.goal;
    state.checkAlpha = state.alpha;
    state.shown = 0;
    go(4);
  } catch (err) {
    showError(err.message);
  } finally {
    label.textContent = old;
    next3.disabled = !state.goal;
  }
}

// ---------- Langkah 4 ----------
const flaggedPoints = (c) => c.plot.qq.sample.map((z, i) => [c.plot.qq.rows[i], z]).filter(([, z]) => Math.abs(z) > Z_FLAG).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));

function renderResults() {
  if (!state.check) {
    root4.replaceChildren(h("div", { class: "note info" }, icon("info"), h("span", {}, "Belum ada hasil. Pilih tujuan di langkah 3, lalu jalankan semua uji.")));
    return;
  }
  const alpha = fmt(state.checkAlpha);
  const sub = h("p", { class: "sub" }, `${GOAL_NAME[state.checkGoal]} · taraf signifikansi α = ${alpha}`);
  const panels = state.check.map((c) => ({ c, el: resultPanel(c), drawn: false }));
  const tabs = h("div", { class: "tabs", role: "tablist", "aria-label": "Hal yang diuji" }, panels.length > 1 ? panels.map((p, i) =>
    h("button", { type: "button", role: "tab", "aria-selected": String(i === state.shown), class: i === state.shown ? "on" : "", onclick: () => { state.shown = i; showPanel(); } }, icon(STATUS[p.c.verdict.status][0]), p.c.label)) : []);
  tabs.hidden = panels.length < 2;
  const holder = h("div", { role: panels.length > 1 ? "tabpanel" : null });
  root4.replaceChildren(sub, tabs, holder);
  function showPanel() {
    [...tabs.children].forEach((b, i) => { b.classList.toggle("on", i === state.shown); b.setAttribute("aria-selected", String(i === state.shown)); });
    const p = panels[state.shown];
    holder.replaceChildren(p.el);
    drawCharts(p);
  }
  showPanel();
}

function drawCharts(p) {
  const c = p.c;
  if (c.verdict.status === "skipped") return;
  if (p.drawn) return void p.el.querySelectorAll(".js-plotly-plot").forEach((e) => Plotly.Plots.resize(e));
  p.drawn = true;
  const q = (s) => p.el.querySelector(s);
  histogram(q(".c-hist"), c.plot.values);
  qq(q(".c-qq"), c.plot.qq, (row, z) => pick(p.el, row, z));
  pp(q(".c-pp"), c.plot.pp);
  boxplot(q(".c-box"), c.plot.values);
}

function pick(panel, row, z) {
  const info = panel.querySelector(".qq-info");
  info.replaceChildren(icon("search"), h("span", {}, h("b", {}, `Responden baris ${row}`), ` · skor terstandar z = ${fmt(z)}. Lihat langkah 5 untuk dugaan penyebabnya.`));
  info.classList.add("hit");
}

function resultPanel(c) {
  const v = c.verdict;
  const [ic, text] = STATUS[v.status];
  const out = h("div", {});
  c.notes.forEach((n) => out.append(h("div", { class: "note info" }, icon("info"), h("span", {}, n))));
  const statusCard = h("div", { class: `status ${v.status}` },
    h("div", { class: "lbl" }, icon(ic), c.label),
    h("div", { class: "big" }, text),
    h("div", { class: "small" }, v.reason || `n = ${c.n}`),
    v.status === "bad" || v.status === "warn" ? h("button", { type: "button", class: "btn small primary", "data-go": "5", style: "margin-top:var(--space-sm)" }, "Lihat penyebabnya", icon("arrow-right")) : null);
  if (v.status === "skipped") {
    out.append(h("div", { class: "grid g2" }, statusCard));
    return out;
  }
  const m = c.moments || {};
  const whyCard = h("div", { class: "card" },
    h("h3", {}, "Kenapa kesimpulannya begini?"),
    h("p", { class: "small" }, RULE[v.rule]),
    m.skew != null ? h("p", { class: "small" }, `Skewness ${fmt(m.skew)} (z = ${fmt(m.z_skew, 1)}) · kurtosis ${fmt(m.kurt)} (z = ${fmt(m.z_kurt, 1)})`) : null,
    h("p", { class: "small" }, h("b", {}, `${v.rejected} dari ${v.total} uji`), " menolak normalitas. Angka ini hanya informasi tambahan; kesimpulan mengikuti aturan di atas, bukan voting."));
  const flagged = flaggedPoints(c);
  const chips = flagged.length
    ? h("div", { class: "chips" }, flagged.slice(0, 12).map(([row, z]) => h("button", { type: "button", class: "chip sus", onclick: () => pick(out, row, z) }, `Baris ${row}`)))
    : h("p", { class: "caption" }, `Tidak ada titik dengan |z| > ${fmt(Z_FLAG, 1)}.`);
  const chart = (cls, title, help, ...extra) => h("div", { class: "card" }, ...titleWithHelp(title, help), h("div", { class: `chart-box ${cls}`, role: "img", "aria-label": title }), ...extra);
  out.append(
    h("div", { class: "grid g2" }, statusCard, whyCard),
    h("div", { class: "grid g2 gap-top" },
      chart("c-hist", "Histogram + kurva normal", HELP.hist),
      chart("c-qq", "Q-Q plot", HELP.qq, h("div", { class: "qq-info caption", "aria-live": "polite" }, "Klik titik merah di grafik, atau tombol di bawah, untuk melihat respondennya."), chips)),
    h("div", { class: "grid g2 gap-top" },
      chart("c-pp", "P-P plot", HELP.pp),
      chart("c-box", "Boxplot", HELP.box)),
    h("details", { open: true }, h("summary", {}, `Semua uji (${c.tests.length})`, icon("chevron-down")), h("div", {}, testTable(c))),
  );
  return out;
}

function testRow(t, c) {
  const alpha = state.checkAlpha;
  let stat = "–";
  let pTxt = "–";
  let result;
  let means;
  if (t.skipped_reason) {
    result = pill("warn", "circle-slash", "Dilewati");
    means = t.skipped_reason + ".";
  } else if (t.id === "skew_kurt") {
    const m = c.moments;
    stat = `${fmt(m.skew)} / ${fmt(m.kurt)}`;
    pTxt = `z = ${fmt(m.z_skew, 1)} / ${fmt(m.z_kurt, 1)}`;
    result = t.rejected ? pill("bad", "circle-x", "Menyimpang") : pill("ok", "circle-check", "Masih aman");
    means = c.n > 300 ? "Batas: |skewness| < 2 dan |kurtosis| < 7." : `Batas: |z| < ${c.n < 50 ? "1,96" : "3,29"}.`;
  } else {
    stat = fmt(t.stat, 3);
    pTxt = fmtP(t.p);
    result = t.rejected ? pill("bad", "circle-x", "Tidak normal") : pill("ok", "circle-check", "Normal");
    means = `p ${t.p < 0.001 ? "< 0,001" : "= " + fmt(t.p, 3)} ${t.rejected ? "<" : "≥"} ${fmt(alpha)} → ${t.rejected ? "berbeda nyata dari" : "tidak berbeda nyata dari"} distribusi normal.`;
  }
  return h("tr", {}, h("td", {}, h("b", {}, t.name), h("div", { class: "caption" }, TEST_INFO[t.id])), h("td", {}, stat), h("td", {}, pTxt), h("td", {}, result),
    h("td", { class: "means" }, means, t.id === "ks_classic" ? h("div", { class: "warn-line" }, icon("triangle-alert"), "Terlalu longgar, sebaiknya tidak dipakai.") : null));
}

function testTable(c) {
  return h("div", { class: "tablewrap", tabindex: "0", role: "region", "aria-label": "Tabel semua uji normalitas" },
    h("table", {}, h("thead", {}, h("tr", {}, ["Uji", "Statistik", "p", "Hasil", "Artinya"].map((t) => h("th", {}, t)))), h("tbody", {}, c.tests.map((t) => testRow(t, c)))));
}

// ---------- Langkah 5 ----------
const SEV = { high: ["circle-x", "high"], medium: ["triangle-alert", "medium"], low: ["info", "low"] };

function rowsTable(tb) {
  const body = tb.rows.slice(0, MAX_ROWS).map((r) => h("tr", { class: "flag" }, r.map((x, i) => h("td", {}, i === 0 ? String(x) : trim(x)))));
  const more = tb.rows.length > MAX_ROWS ? h("p", { class: "caption" }, `dan ${tb.rows.length - MAX_ROWS} baris lainnya`) : null;
  return h("div", {}, h("div", { class: "tablewrap" }, h("table", {}, h("thead", {}, h("tr", {}, tb.columns.map((c) => h("th", {}, c)))), h("tbody", {}, body))), more);
}

function renderCauses() {
  if (!state.check) {
    root5.replaceChildren(h("div", { class: "note info" }, icon("info"), h("span", {}, "Belum ada hasil. Jalankan semua uji di langkah 3 dulu.")));
    return;
  }
  const out = [h("p", { class: "sub" }, "Baris yang ditandai hanya sorotan untuk kamu periksa. Tidak ada data yang dihapus.")];
  for (const c of state.check) {
    const [ic, text] = STATUS[c.verdict.status];
    out.push(h("h3", { class: "target" }, c.label, " ", pill(c.verdict.status, ic, text)));
    if (!c.findings.length) {
      out.push(h("div", { class: `note ${c.verdict.status === "skipped" ? "info" : "ok"}` }, icon(c.verdict.status === "skipped" ? "info" : "circle-check"), h("span", {}, c.verdict.status === "skipped" ? c.verdict.reason : "Tidak ada penyebab yang menonjol.")));
      continue;
    }
    out.push(h("div", { class: "card flush" }, c.findings.map((f) => {
      const [sic, cls] = SEV[f.severity];
      return h("div", { class: "finding" }, h("div", { class: `n ${cls}` }, icon(sic)),
        h("div", { class: "grow" }, h("h3", {}, f.title), h("p", { class: "small muted" }, f.detail),
          f.table ? rowsTable(f.table) : null,
          f.id === "data_error" || f.id === "unreversed_item" ? h("button", { type: "button", class: "btn small", "data-go": "2", style: "margin-top:var(--space-sm)" }, "Periksa di langkah 2") : null));
    })));
  }
  root5.replaceChildren(...out);
}

// ---------- Pemasangan ----------
let root3, root4, root5, next3;

export function initResults(deps) {
  ({ state, go, showError, h, icon } = deps);
  root3 = document.getElementById("step3");
  root4 = document.getElementById("step4");
  root5 = document.getElementById("step5");
  next3 = document.getElementById("next3");
  next3.addEventListener("click", runCheck);
  document.addEventListener("step", (e) => {
    if (e.detail === 3) renderGoals();
    else if (e.detail === 4) renderResults();
    else if (e.detail === 5) renderCauses();
  });
}
