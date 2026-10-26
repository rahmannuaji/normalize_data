// Pyodide + paket cekdata di Web Worker, agar hitungan berat (mis. bootstrap 5.000 sampel ulang pada 10.000 baris)
// tidak membekukan halaman. Hanya engine.js yang berbicara dengan worker ini.
// Data pengguna hanya ditulis ke filesystem virtual Pyodide di memori browser, tidak dikirim ke mana pun.
importScripts("https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js");

const VERSION = new URL(location.href).searchParams.get("v");
const PY_FILES = ["__init__.py", "io.py", "prep.py", "target.py", "normality.py", "diagnose.py", "remedies.py", "report.py", "api.py"];
const PKG_DIR = "/home/pyodide/cekdata";

let pyodide;
let dispatch; // (name, json) => json, dibuat sekali agar tidak membuat PyProxy baru tiap panggilan

const loading = (async () => {
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
})();

loading.then(() => postMessage({ id: 0 }), (e) => postMessage({ id: 0, fail: String(e?.stack || e) }));

// Pesan diproses berurutan: dispatch sinkron, jadi panggilan berikutnya menunggu yang sebelumnya selesai.
onmessage = async ({ data: { id, op, name, payload, path, bytes } }) => {
  try {
    await loading;
    if (op === "write") {
      pyodide.FS.writeFile(path, bytes);
      postMessage({ id });
    } else {
      postMessage({ id, out: dispatch(name, payload) });
    }
  } catch (e) {
    postMessage({ id, fail: String(e?.stack || e) });
  }
};
