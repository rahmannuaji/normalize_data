// State UI dan navigasi langkah. Isi langkah 1–7 dirender ke #step1..#step7 (Task 10–12).
import { ready, call, writeFile } from "./engine.js";
import { initResults } from "./results.js";
import { initRemedy } from "./remedy.js";

const AUTHOR = ""; // nama pembuat untuk footer; biarkan kosong sampai diberikan pemilik proyek

export const state = {};

const pages = [...document.querySelectorAll("section.page")];
const stepsEl = document.getElementById("steps");
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");
let cur = -1;

for (const p of pages.slice(1)) {
  const b = document.createElement("button");
  b.type = "button";
  b.className = "step";
  b.dataset.go = p.dataset.step;
  b.innerHTML = `<b>${p.dataset.step}</b>`;
  b.append(p.dataset.title);
  stepsEl.append(b);
}

// Semua elemen [data-go] (stepper, tombol Kembali/Lanjut, logo) berpindah langkah lewat go().
document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-go]");
  if (!t || t.disabled) return;
  e.preventDefault();
  go(Number(t.dataset.go));
});

export function go(step) {
  if (step > 1 && !state.table) {
    go(1);
    showError("Masukkan datamu dulu di langkah 1.");
    return;
  }
  const first = cur < 0;
  cur = step;
  for (const p of pages) {
    p.classList.toggle("on", Number(p.dataset.step) === step);
    p.querySelector(":scope > .page-error")?.remove();
  }
  refreshNav();
  stepsEl.hidden = step === 0;
  if (!first) {
    scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" });
    pages[step].querySelector("h1, h2")?.focus({ preventScroll: true });
  }
  document.dispatchEvent(new CustomEvent("step", { detail: step })); // langkah 3–5 menggambar isinya (results.js)
}

// Perbarui stepper (aktif/selesai/nonaktif) tanpa berpindah halaman; dipanggil setelah state.table berubah.
export function refreshNav() {
  [...stepsEl.children].forEach((b, i) => {
    const n = i + 1;
    b.classList.toggle("on", n === cur);
    b.classList.toggle("done", n < cur);
    b.disabled = n > 1 && !state.table;
    if (n === cur) b.setAttribute("aria-current", "step");
    else b.removeAttribute("aria-current");
  });
}

export function showError(msg) {
  const page = pages[cur];
  page.querySelector(":scope > .page-error")?.remove();
  const note = document.createElement("div");
  note.className = "note bad page-error";
  note.setAttribute("role", "alert");
  note.innerHTML = '<svg class="ic" aria-hidden="true"><use href="assets/icons.svg#circle-x"/></svg><span></span>';
  note.querySelector("span").textContent = msg;
  page.prepend(note);
  note.scrollIntoView({ block: "nearest", behavior: reduceMotion.matches ? "auto" : "smooth" });
}

ready().then(
  () => {
    document.getElementById("loadbar").hidden = true;
    document.getElementById("next1").disabled = false;
  },
  (err) => {
    const bar = document.getElementById("loadbar");
    bar.classList.add("bad");
    bar.querySelector("p").innerHTML = '<svg class="ic" aria-hidden="true"><use href="assets/icons.svg#circle-x"/></svg><span></span>';
    bar.querySelector("span").textContent = err.message;
  },
);

if (AUTHOR) {
  document.getElementById("author").textContent = AUTHOR;
  document.getElementById("footer").hidden = false;
}

// ---------- Pembantu DOM ----------
const SVG_NS = "http://www.w3.org/2000/svg";
function h(tag, props = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (v == null || v === false) continue;
    if (k === "class") e.className = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const c of kids.flat()) if (c != null && c !== false) e.append(c);
  return e;
}
function icon(name) {
  const s = document.createElementNS(SVG_NS, "svg");
  s.setAttribute("class", "ic");
  s.setAttribute("aria-hidden", "true");
  const u = document.createElementNS(SVG_NS, "use");
  u.setAttribute("href", `assets/icons.svg#${name}`);
  s.append(u);
  return s;
}
const num = (n) => String(Math.round(n * 100) / 100).replace(".", ",").replace("-", "−");
const cell = (v) => (v == null ? "" : typeof v === "number" ? String(v).replace(".", ",") : String(v));
const MAX_WARN = 20;
function note(kind, ic, ...kids) {
  return h("div", { class: `note ${kind}` }, icon(ic), h("span", {}, ...kids));
}
function capped(list, render) {
  const out = list.slice(0, MAX_WARN).map(render);
  if (list.length > MAX_WARN) out.push(h("p", { class: "caption" }, `dan ${list.length - MAX_WARN} lainnya`));
  return out;
}

// ---------- Langkah 1: masukkan data ----------
const root1 = document.getElementById("step1");
const prev = h("div", { id: "prev", "aria-live": "polite" });
const TABS = [["upload", "Upload file", "upload"], ["ketik", "Ketik sendiri", "keyboard"], ["contoh", "Data contoh", "flask-conical"]];
const tabBtns = {};
const panels = {};
const tabBar = h("div", { class: "tabs", role: "tablist" });
for (const [id, label, ic] of TABS) {
  tabBtns[id] = h("button", { type: "button", role: "tab", onclick: () => showTab(id) }, icon(ic), label);
  panels[id] = h("div", { role: "tabpanel" });
  tabBar.append(tabBtns[id]);
}
export function showTab(id) {
  for (const [k] of TABS) {
    tabBtns[k].classList.toggle("on", k === id);
    tabBtns[k].setAttribute("aria-selected", k === id);
    panels[k].hidden = k !== id;
  }
}
document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-tab]");
  if (t) showTab(t.dataset.tab);
});

// Upload
const fileInput = h("input", { type: "file", accept: ".csv,.xlsx,.xls", class: "vh", onchange: () => fileInput.files[0] && loadFile(fileInput.files[0]) });
const drop = h("label", { class: "drop" }, icon("file-spreadsheet"), h("div", {}, h("b", {}, "Seret file ke sini atau klik untuk memilih")), h("div", { class: "caption" }, ".csv, .xlsx, .xls · baris pertama berisi nama kolom"), fileInput);
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("over"); });
drop.addEventListener("dragleave", () => drop.classList.remove("over"));
drop.addEventListener("drop", (e) => {
  e.preventDefault();
  drop.classList.remove("over");
  if (e.dataTransfer.files[0]) loadFile(e.dataTransfer.files[0]);
});
const sheetBox = h("div", { hidden: true });
panels.upload.append(drop, sheetBox);

async function loadFile(file, sheet = null) {
  try {
    const path = await busy(async () => writeFile(file.name, new Uint8Array(await file.arrayBuffer())));
    await loadPath(path, file.name, sheet, file);
  } catch (err) {
    showError(err.message);
  }
}

async function busy(fn) {
  prev.replaceChildren(note("info", "info", "Membaca data…"));
  try {
    return await fn();
  } catch (err) {
    prev.replaceChildren();
    throw err;
  }
}

async function loadPath(path, name, sheet, file) {
  const res = await busy(() => call("load_table", { path, sheet }));
  const sameCols = state.table && state.table.columns.join("\u0000") === res.columns.join("\u0000");
  state.table = { ...res, path, name };
  if (!sameCols) resetVariables();
  refreshNav();
  renderPreview();
  renderSheetPicker(file, sheet);
  renderStep2();
  runPrepare();
}

function renderSheetPicker(file, sheet) {
  sheetBox.replaceChildren();
  const sheets = state.table.sheets || [];
  sheetBox.hidden = sheets.length < 2 || !file;
  if (sheetBox.hidden) return;
  const sel = h("select", { class: "inp", id: "sheetSel", onchange: () => loadFile(file, sel.value) }, sheets.map((s) => h("option", { value: s, selected: s === (sheet || sheets[0]) }, s)));
  sheetBox.append(h("div", { class: "field" }, h("label", { for: "sheetSel" }, "File ini punya beberapa sheet. Pakai yang mana?"), sel));
}

function renderPreview() {
  const t = state.table;
  const sheetTxt = t.sheets && t.sheets.length > 1 ? ` (sheet "${document.getElementById("sheetSel")?.value || t.sheets[0]}")` : "";
  const table = h("table", {}, h("thead", {}, h("tr", {}, t.columns.map((c) => h("th", {}, c)))), h("tbody", {}, t.preview.slice(0, 10).map((r) => h("tr", {}, r.map((v) => h("td", {}, cell(v)))))));
  prev.replaceChildren(
    note("ok", "circle-check", h("b", {}, t.name), ` terbaca: ${t.n_rows} baris, ${t.columns.length} kolom${sheetTxt}.`),
    ...capped(t.warnings || [], (w) => note("warn", "triangle-alert", w)),
    h("div", { class: "tablewrap", tabindex: "0", role: "region", "aria-label": "Pratinjau data" }, table),
    h("p", { class: "caption" }, t.n_rows > 10 ? "Pratinjau 10 baris pertama. " : "", "Datamu hanya diproses di browser ini dan tidak dikirim ke mana pun."),
  );
}

// Ketik sendiri
const manual = { ny: 1, nx: 2, rows: 20, data: [] };
const manualTable = h("div", { class: "tablewrap" });
const manualSel = (id, label, from, to, key) => {
  const s = h("select", { class: "inp", id, onchange: () => { manual[key] = Number(s.value); renderManual(); } }, Array.from({ length: to - from + 1 }, (_, i) => h("option", { value: from + i, selected: from + i === manual[key] }, from + i)));
  return h("div", { class: "field" }, h("label", { for: id }, label), s);
};
const rowsInput = h("input", { class: "inp", id: "mRows", type: "number", min: 1, max: 1000, value: manual.rows, onchange: () => { manual.rows = Math.min(1000, Math.max(1, Number(rowsInput.value) || 1)); renderManual(); } });
function manualHeaders() {
  return [...Array.from({ length: manual.ny }, (_, i) => `Y${i + 1}`), ...Array.from({ length: manual.nx }, (_, i) => `X${i + 1}`)];
}
function renderManual(focus) {
  const cols = manualHeaders();
  rowsInput.value = manual.rows;
  manual.data = Array.from({ length: manual.rows }, (_, r) => Array.from({ length: cols.length }, (_, c) => manual.data[r]?.[c] ?? ""));
  const body = manual.data.map((row, r) => h("tr", {}, h("td", {}, r + 1), row.map((v, c) => h("td", { contenteditable: "plaintext-only", "data-r": r, "data-c": c, role: "textbox", "aria-label": `${cols[c]} baris ${r + 1}` }, v))));
  manualTable.replaceChildren(h("table", {}, h("thead", {}, h("tr", {}, h("th", {}, "#"), cols.map((c) => h("th", {}, c)))), h("tbody", {}, body)));
  if (focus) manualTable.querySelector(`td[data-r="${focus[0]}"][data-c="${focus[1]}"]`)?.focus();
}
manualTable.addEventListener("input", (e) => {
  const td = e.target.closest("td[data-r]");
  if (td) manual.data[td.dataset.r][td.dataset.c] = td.textContent;
});
manualTable.addEventListener("paste", (e) => {
  const td = e.target.closest("td[data-r]");
  if (!td) return;
  e.preventDefault();
  const lines = e.clipboardData.getData("text/plain").replace(/\r/g, "").replace(/\n$/, "").split("\n").map((l) => l.split("\t"));
  const r0 = Number(td.dataset.r);
  const c0 = Number(td.dataset.c);
  manual.rows = Math.min(1000, Math.max(manual.rows, r0 + lines.length));
  manual.data = Array.from({ length: manual.rows }, (_, r) => manual.data[r] ?? []);
  lines.forEach((cells, i) => cells.forEach((v, j) => {
    if (c0 + j < manualHeaders().length && r0 + i < manual.rows) manual.data[r0 + i][c0 + j] = v.trim();
  }));
  renderManual([r0, c0]);
});
const useManual = h("button", { type: "button", class: "btn primary", onclick: () => submitManual() }, "Pakai data ini");
async function submitManual() {
  const cols = manualHeaders();
  // Baris kosong di tengah tetap dikirim agar nomor baris dari mesin = nomor baris di tabel; hanya baris kosong di ujung dibuang.
  const rows = manual.data.slice();
  while (rows.length && rows[rows.length - 1].every((v) => String(v).trim() === "")) rows.pop();
  if (!rows.length) return showError("Isi minimal satu sel dulu.");
  const clean = (v) => String(v ?? "").replace(/[;\n\r\t]/g, " ").trim();
  const csv = [cols, ...rows].map((r) => r.map(clean).join(";")).join("\n");
  try {
    const path = await busy(() => writeFile("manual.csv", new TextEncoder().encode(csv)));
    await loadPath(path, "Data ketikanmu", null, null);
  } catch (err) {
    showError(err.message);
  }
}
panels.ketik.append(h("div", { class: "card" },
  h("div", { class: "grid g3" }, manualSel("mY", "Jumlah variabel Y", 1, 3, "ny"), manualSel("mX", "Jumlah variabel X", 0, 10, "nx"), h("div", { class: "field" }, h("label", { for: "mRows" }, "Jumlah responden (baris)"), rowsInput)),
  h("div", { style: "margin-top:var(--space-md)" }, manualTable),
  h("p", { class: "caption" }, "Bisa langsung Ctrl+V dari Excel: tempel di sel mana pun, isinya menyebar ke kolom dan baris di sebelahnya."),
  useManual));
renderManual();

// Contoh
const EXAMPLES = [
  ["kuesioner_psikologi.csv", "Kuesioner psikologi (150 responden)", "Dukungan sosial dan kesejahteraan psikologis. Ada efek plafon dan satu item belum dibalik.", "flask-conical"],
  ["pretest_posttest.csv", "Pretest–posttest", "Data berpasangan, cocok untuk mencoba uji-t berpasangan dan Wilcoxon.", "repeat"],
];
panels.contoh.append(h("div", { class: "grid g2" }, EXAMPLES.map(([file, title, desc, ic]) =>
  h("button", { type: "button", class: "opt", onclick: () => loadExample(file) }, icon(ic), h("b", {}, title), h("small", {}, desc)))));
async function loadExample(file) {
  try {
    const path = await busy(async () => {
      const res = await fetch(`contoh/${file}`);
      if (!res.ok) throw new Error("Data contoh gagal dimuat. Muat ulang halaman, lalu coba lagi.");
      return writeFile(file, new Uint8Array(await res.arrayBuffer()));
    });
    await loadPath(path, file, null, null);
  } catch (err) {
    showError(err.message);
  }
}

root1.append(tabBar, panels.upload, panels.ketik, panels.contoh, prev);
showTab("upload");

// ---------- Langkah 2: atur variabel ----------
const root2 = document.getElementById("step2");
state.variables = [];
state.group = null;
state.prep = null;
const LIMIT = { Y: 3, X: 10 };
const varsBox = h("div", { class: "grid g2" });
const groupBox = h("div", { class: "card", style: "margin-top:var(--space-md)" });
const addBox = h("div", { class: "actions", style: "margin-top:var(--space-md)" });
const prepBox = h("div", { id: "prepOut", "aria-live": "polite", style: "margin-top:var(--space-md)" });
root2.append(varsBox, addBox, groupBox, prepBox);

function nextName(role) {
  let i = 1;
  while (state.variables.some((v) => v.name === role + i)) i++;
  return role + i;
}
function newVar(role) {
  return { name: nextName(role), role, columns: [], combine: "sum", reversed: [], scale: null, ui: { mode: "items", smin: "", smax: "" } };
}
function resetVariables() {
  state.variables = [];
  state.variables.push(newVar("Y"), newVar("X"));
  state.group = null;
  state.prep = null;
}
const count = (role) => state.variables.filter((v) => v.role === role).length;
let focusKey = null;

function renderStep2() {
  if (!state.table) return;
  const cols = state.table.columns;
  varsBox.replaceChildren(...state.variables.map((v, i) => varCard(v, i, cols)));
  addBox.replaceChildren(
    ...["X", "Y"].map((role) => h("button", { type: "button", class: "btn small", disabled: count(role) >= LIMIT[role], "data-k": `add${role}`, onclick: () => { state.variables.push(newVar(role)); focusKey = `add${role}`; renderStep2(); schedulePrepare(); } }, icon("plus"), `Tambah variabel ${role}`)),
  );
  const gsel = h("select", { class: "inp", id: "grp", onchange: () => { state.group = gsel.value || null; schedulePrepare(); } },
    h("option", { value: "" }, "Tanpa kelompok"), cols.map((c) => h("option", { value: c, selected: c === state.group }, c)));
  groupBox.replaceChildren(h("div", { class: "field" }, h("label", { for: "grp" }, "Kolom kelompok (opsional)"), gsel, h("span", { class: "caption" }, "Dipakai untuk membandingkan kelompok, misalnya jenis kelamin atau kelas.")));
  if (focusKey) document.querySelector(`[data-k="${focusKey}"]`)?.focus();
  focusKey = null;
}

function changed(key) {
  focusKey = key;
  renderStep2();
  schedulePrepare();
}

function varCard(v, i, cols) {
  const items = v.ui.mode === "items";
  const head = h("div", { class: "vhead" },
    h("div", { class: "field grow" }, h("label", { for: `vn${i}` }, "Nama variabel"), h("input", { class: "inp", id: `vn${i}`, value: v.name, oninput: (e) => { v.name = e.target.value; schedulePrepare(); } })),
    h("span", { class: `pill ${v.role === "Y" ? "ok" : "warn"}` }, v.role === "Y" ? "Dependen (Y)" : "Independen (X)"));
  const mode = h("div", { class: "tabs", role: "group", "aria-label": "Cara membaca kolom" }, [["single", "Satu kolom"], ["items", "Gabungan item"]].map(([m, label]) =>
    h("button", { type: "button", class: (m === "items") === items ? "on" : "", "aria-pressed": (m === "items") === items, "data-k": `m${i}${m}`, onclick: () => { v.ui.mode = m; if (m === "single") { v.columns = v.columns.slice(0, 1); v.reversed = []; } changed(`m${i}${m}`); } }, label)));
  const body = [];
  if (!items) {
    const sel = h("select", { class: "inp", "aria-label": `Kolom untuk ${v.name}`, onchange: () => { v.columns = sel.value ? [sel.value] : []; schedulePrepare(); } },
      h("option", { value: "" }, "Pilih kolom"), cols.map((c) => h("option", { value: c, selected: v.columns[0] === c }, c)));
    body.push(sel);
  } else {
    body.push(h("p", { class: "caption" }, "Klik item untuk memilih. Tombol ↺ di item terpilih menandainya unfavorable (skornya dibalik, misalnya 1↔5 dan 2↔4). Klik kanan pada item juga bisa."));
    body.push(h("div", {}, cols.map((c, j) => chip(v, c, `${i}_${j}`))));
    const sminI = h("input", { class: "inp", type: "number", "aria-label": "Skor terendah", value: v.ui.smin, oninput: () => scaleChanged(v, sminI, smaxI) });
    const smaxI = h("input", { class: "inp", type: "number", "aria-label": "Skor tertinggi", value: v.ui.smax, oninput: () => scaleChanged(v, sminI, smaxI) });
    const comb = h("select", { class: "inp", id: `vc${i}`, onchange: () => { v.combine = comb.value; schedulePrepare(); } },
      h("option", { value: "sum", selected: v.combine === "sum" }, "Dijumlahkan"), h("option", { value: "mean", selected: v.combine === "mean" }, "Rata-rata"));
    body.push(h("div", { class: "grid g2 vrow" },
      h("div", { class: "field" }, h("label", { for: `vc${i}` }, "Gabungkan dengan"), comb),
      h("div", { class: "field" }, h("span", {}, "Skala jawaban (opsional)"), h("div", { class: "scale" }, sminI, h("span", {}, "sampai"), smaxI))));
  }
  const canRemove = v.role === "X" || count("Y") > 1;
  const foot = canRemove ? h("button", { type: "button", class: "btn small", "data-k": "rm", onclick: () => { state.variables.splice(i, 1); changed("addX"); } }, `Hapus ${v.name || "variabel"}`) : null;
  return h("div", { class: "card" }, head, mode, ...body, foot);
}

function scaleChanged(v, a, b) {
  v.ui.smin = a.value;
  v.ui.smax = b.value;
  schedulePrepare();
}

function chip(v, c, key) {
  const on = v.columns.includes(c);
  const rev = v.reversed.includes(c);
  const toggleRev = () => { v.reversed = rev ? v.reversed.filter((x) => x !== c) : [...v.reversed, c]; changed(`r${key}`); };
  const sel = h("button", { type: "button", "aria-pressed": on, "data-k": `c${key}`, onclick: () => { v.columns = on ? v.columns.filter((x) => x !== c) : [...v.columns, c]; if (on) v.reversed = v.reversed.filter((x) => x !== c); changed(`c${key}`); } }, c);
  const el = h("span", { class: `chip grp${on ? " sel" : ""}${rev ? " rev" : ""}` }, sel);
  if (on) el.append(h("button", { type: "button", class: "rv", "aria-pressed": rev, "aria-label": `Tandai ${c} sebagai unfavorable`, "data-k": `r${key}`, onclick: toggleRev }, icon("rotate-ccw")));
  if (on) el.addEventListener("contextmenu", (e) => { e.preventDefault(); toggleRev(); });
  return el;
}

// Spesifikasi untuk engine: hanya variabel yang sudah punya kolom.
function specs() {
  return state.variables.filter((v) => v.columns.length).map((v) => {
    const a = parseFloat(v.ui.smin);
    const b = parseFloat(v.ui.smax);
    return { name: v.name.trim() || v.role, role: v.role, columns: [...v.columns], combine: v.ui.mode === "items" ? v.combine : "sum", reversed: v.ui.mode === "items" ? v.reversed.filter((c) => v.columns.includes(c)) : [], scale: Number.isFinite(a) && Number.isFinite(b) && a < b ? [a, b] : null };
  });
}

let timer = 0;
let seq = 0;
function schedulePrepare() {
  clearTimeout(timer);
  timer = setTimeout(runPrepare, 300);
}
async function runPrepare() {
  const mine = ++seq;
  const vars = specs();
  if (!vars.length) {
    state.prep = null;
    prepBox.replaceChildren(note("info", "info", "Pilih kolom untuk minimal satu variabel, nanti kami cek isinya di sini."));
    return;
  }
  try {
    const res = await call("prepare", { variables: vars, group: state.group });
    if (mine !== seq) return;
    state.prep = res;
    state.check = null; // variabel berubah, hasil uji lama tidak berlaku lagi
    renderPrep(res);
  } catch (err) {
    if (mine === seq) showError(err.message);
  }
}

async function fixCell(w, input) {
  const value = parseFloat(input.value.replace(",", "."));
  if (!Number.isFinite(value)) return showError("Isi nilai pengganti berupa angka.");
  try {
    await call("set_cell", { row: w.row, column: w.column, value });
    await runPrepare();
  } catch (err) {
    showError(err.message);
  }
}

function renderPrep(p) {
  const out = [];
  const neg = p.warnings.filter((w) => w.kind === "negative_item_total");
  const oor = p.warnings.filter((w) => w.kind === "out_of_range");
  const nn = p.warnings.filter((w) => w.kind === "non_numeric");
  out.push(...capped(neg, (w) => note("warn", "triangle-alert",
    h("b", {}, w.item), ` berkorelasi negatif dengan total ${w.variable} (r = ${num(w.r)}). Kemungkinan item unfavorable yang belum dibalik. `,
    h("button", { type: "button", class: "btn small", onclick: () => reverseItem(w) }, `Balik skor ${w.item}`))));
  out.push(...capped(oor, (w) => {
    const inp = h("input", { class: "inp fix", inputmode: "decimal", "aria-label": `Nilai pengganti baris ${w.row} kolom ${w.column}` });
    return note("warn", "triangle-alert", `Baris ${w.row} berisi nilai ${cell(w.value)} di `, h("b", {}, w.column), " (di luar skala). Mungkin salah ketik. ",
      h("span", { class: "fixrow" }, inp, h("button", { type: "button", class: "btn small", onclick: () => fixCell(w, inp) }, "Perbaiki")));
  }));
  out.push(...capped(nn, (w) => note("warn", "triangle-alert", `Kolom `, h("b", {}, w.column), ` punya ${w.count} sel yang bukan angka. Barisnya tidak diikutkan.`)));
  if (p.n_dropped > 0) {
    const rows = p.dropped_rows.slice(0, MAX_WARN).join(", ") + (p.dropped_rows.length > MAX_WARN ? `, dan ${p.dropped_rows.length - MAX_WARN} lainnya` : "");
    out.push(note("info", "info", h("b", {}, `${p.n_dropped} baris dikeluarkan`), ` karena ada sel kosong atau bukan angka (baris ${rows}). `, h("b", {}, `${p.n_used} dianalisis.`)));
  } else {
    out.push(note("ok", "circle-check", h("b", {}, `${p.n_used} baris dianalisis.`), " Tidak ada baris yang dikeluarkan."));
  }
  prepBox.replaceChildren(...out);
}

function reverseItem(w) {
  const v = state.variables.find((x) => (x.name.trim() || x.role) === w.variable);
  if (!v) return;
  if (!v.reversed.includes(w.item)) v.reversed.push(w.item);
  renderStep2();
  runPrepare();
}

initResults({ state, go, showError, h, icon });
initRemedy({ state, go, showError, h, icon });
go(0);
