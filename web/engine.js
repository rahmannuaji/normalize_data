// Mesin statistik: satu-satunya jembatan JS ↔ Python. Pyodide berjalan di Web Worker (engine-worker.js) supaya
// halaman tetap responsif selama hitungan berat; API modul ini (ready, call, writeFile) tetap sama.
// Data pengguna hanya ditulis ke filesystem virtual Pyodide di memori browser, tidak dikirim ke mana pun.

// Naikkan VERSION setiap rilis (juga ?v= pada import dan index.html) agar browser tidak memakai cache lama.
const VERSION = "7";
const API_NAMES = ["load_table", "set_cell", "prepare", "check", "remedy", "report", "export_scores"];
const LOAD_FAILED = "Mesin statistik gagal dimuat. Periksa koneksi internetmu, lalu muat ulang halaman.";
const CRASHED = "Terjadi kesalahan di mesin statistik. Coba muat ulang halaman.";
const BUSY_DELAY = 300; // ms; indikator hanya untuk panggilan yang terasa lama, agar tidak berkedip saat mengetik

const worker = new Worker(`engine-worker.js?v=${VERSION}`);
const pending = new Map();
let seq = 0;
let settle;
const loading = new Promise((resolve, reject) => (settle = { resolve, reject }));

// Event "engine-busy" (detail: true/false) untuk indikator "Menghitung…" di app.js.
let active = 0;
let busyTimer = 0;
function busy(delta) {
  active += delta;
  clearTimeout(busyTimer);
  busyTimer = setTimeout(() => document.dispatchEvent(new CustomEvent("engine-busy", { detail: active > 0 })), active ? BUSY_DELAY : 0);
}

worker.onmessage = ({ data }) => {
  if (data.id === 0) {
    if (!data.fail) return settle.resolve();
    console.error(data.fail);
    return settle.reject(new Error(LOAD_FAILED));
  }
  const p = pending.get(data.id);
  pending.delete(data.id);
  busy(-1);
  if (data.fail) p.reject(data.fail);
  else p.resolve(data);
};
worker.onerror = (e) => {
  console.error(e.message);
  settle.reject(new Error(LOAD_FAILED));
  for (const p of pending.values()) p.reject(e.message);
  pending.clear();
  busy(-active);
};

function send(msg) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    pending.set(id, { resolve, reject });
    busy(1);
    worker.postMessage({ id, ...msg });
  });
}

export function ready() {
  return loading;
}

export async function call(name, args = {}) {
  await loading;
  if (!API_NAMES.includes(name)) throw new Error(`Fungsi "${name}" tidak dikenal.`);
  let out;
  try {
    out = JSON.parse((await send({ op: "call", name, payload: JSON.stringify(args) })).out);
  } catch (e) {
    console.error(e);
    throw new Error(CRASHED);
  }
  if (out && out.error) {
    if (out.detail) console.error(out.detail); // rincian teknis hanya untuk konsol, tidak ditampilkan ke pengguna
    throw new Error(out.error);
  }
  return out;
}

export async function writeFile(name, bytes) {
  await loading;
  const path = `/tmp/${String(name).replace(/[\\/]/g, "_")}`;
  try {
    await send({ op: "write", path, bytes });
  } catch (e) {
    console.error(e);
    throw new Error(CRASHED);
  }
  return path;
}
