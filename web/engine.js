// Mesin statistik: Pyodide + paket cekdata. Satu-satunya jembatan JS ↔ Python.
// Data pengguna hanya ditulis ke filesystem virtual Pyodide di memori browser, tidak dikirim ke mana pun.

// Naikkan VERSION setiap rilis (juga ?v= pada import dan index.html) agar browser tidak memakai cache lama.
const VERSION = "2";
const PY_FILES = ["__init__.py", "io.py", "prep.py", "target.py", "normality.py", "diagnose.py", "remedies.py", "report.py", "api.py"];
const API_NAMES = ["load_table", "set_cell", "prepare", "check", "remedy", "report", "export_scores"];
const PKG_DIR = "/home/pyodide/cekdata";
const LOAD_FAILED = "Mesin statistik gagal dimuat. Periksa koneksi internetmu, lalu muat ulang halaman.";

let pyodide;
let dispatch; // (name, json) => json, dibuat sekali agar tidak membuat PyProxy baru tiap panggilan

const loading = (async () => {
  try {
    pyodide = await loadPyodide();
    await pyodide.loadPackage(["numpy", "pandas", "scipy", "statsmodels", "micropip"]);
    // openpyxl tidak ada di distribusi Pyodide 0.27.7, jadi dipasang dari PyPI bersama xlrd (murni Python).
    await pyodide.pyimport("micropip").install(["openpyxl==3.1.5", "xlrd==2.0.1"]);
    pyodide.FS.mkdirTree(PKG_DIR);
    await Promise.all(PY_FILES.map(async (f) => {
      const res = await fetch(`py/cekdata/${f}?v=${VERSION}`);
      if (!res.ok) throw new Error(`py/cekdata/${f}: HTTP ${res.status}`);
      pyodide.FS.writeFile(`${PKG_DIR}/${f}`, await res.text());
    }));
    dispatch = pyodide.runPython("import cekdata.api as _api\nlambda name, payload: getattr(_api, name)(payload)");
  } catch (e) {
    console.error(e);
    throw new Error(LOAD_FAILED);
  }
})();

export function ready() {
  return loading;
}

export async function call(name, args = {}) {
  await loading;
  if (!API_NAMES.includes(name)) throw new Error(`Fungsi "${name}" tidak dikenal.`);
  let out;
  try {
    out = JSON.parse(dispatch(name, JSON.stringify(args)));
  } catch (e) {
    console.error(e);
    throw new Error("Terjadi kesalahan di mesin statistik. Coba muat ulang halaman.");
  }
  if (out && out.error) throw new Error(out.error);
  return out;
}

export async function writeFile(name, bytes) {
  await loading;
  const path = `/tmp/${String(name).replace(/[\\/]/g, "_")}`;
  pyodide.FS.writeFile(path, bytes);
  return path;
}
