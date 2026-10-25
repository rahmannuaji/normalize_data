# Normalin

Normalin mengecek normalitas data skripsi atau tesis, menunjukkan penyebab data tidak normal, lalu membantu memilih analisis yang tetap sah. Semua perhitungan statistik berjalan di browser lewat Python (Pyodide), tanpa server.

## Menjalankan lokal

```
python -m http.server 8000 -d web
```

Buka http://localhost:8000. Pertama kali dibuka, Pyodide dan paket statistik diunduh dari CDN, jadi perlu internet.

## Menjalankan test

Buat venv dari `requirements-dev.txt` (versinya disamakan dengan paket Pyodide 0.27), lalu jalankan pytest:

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest
```

## Privasi

Data yang kamu unggah tidak dikirim ke mana pun. File dibaca dan dihitung di memori browser. Request jaringan hanya untuk memuat aplikasi dan pustaka: `cdn.jsdelivr.net` (Pyodide, Plotly), `fonts.googleapis.com` dan `fonts.gstatic.com` (font), serta `pypi.org` dan `files.pythonhosted.org` (openpyxl dan xlrd untuk membaca Excel; tidak membawa data).

## Deploy ke GitHub Pages

Workflow `.github/workflows/pages.yml` menerbitkan folder `web/` setiap push ke `main` atau lewat Run workflow manual. Sekali saja, aktifkan di repo: Settings > Pages > Build and deployment > Source: **GitHub Actions**.

Setiap rilis, naikkan `VERSION` di `web/engine.js` dan `?v=` pada `import` di `web/*.js` serta `<script>` di `web/index.html` (cari dengan `grep -rn "?v=" web`). Tanpa ini browser bisa memakai `engine.js` atau file Python lama dari cache.

## Belum diisi

Konstanta `AUTHOR` di `web/app.js` sengaja kosong. Selama kosong, footer tidak menampilkan nama pembuat. Isi dengan namamu saat siap.
