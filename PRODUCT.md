# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Static HTML/CSS/JavaScript tanpa framework dan tanpa build step; logika statistik di Python yang dijalankan di browser lewat Pyodide; grafik Plotly.js; hosting statis (GitHub Pages). Dipilih Claude, disetujui pengguna (desain 2026-10-25).

## Users

Mahasiswa S1 di Indonesia yang sedang mengerjakan Bab IV skripsi, terutama mahasiswa psikologi dengan data kuesioner skala Likert (30–400 responden, beberapa skala berisi 10–40 item, ada item favorable dan unfavorable). Statistik dasar mereka terbatas, mereka terbiasa dengan Excel dan SPSS, dan cemas menghadapi istilah teknis serta dosen penguji. Situasinya: hasil uji prasyarat menyatakan "data tidak normal" dan mereka tidak tahu harus berbuat apa.

## Product Purpose

Normalin membantu mahasiswa memahami kenapa datanya tidak normal dan memilih langkah yang sah secara statistik, lalu menghasilkan teks yang siap ditempel ke Bab IV. Berhasil berarti mahasiswa bisa mempertanggungjawabkan keputusannya di depan dosen penguji, bukan sekadar mendapat p > 0,05.

## Positioning

Normalin bukan alat untuk membuat data jadi normal. Posisinya: "Datamu tidak normal? Ini artinya, dan ini analisis yang tetap sah." Normalin memeriksa hal yang sebenarnya harus normal sesuai analisis (misalnya residual untuk regresi), menunjukkan responden atau item penyebabnya, menolak cara-cara manipulatif, dan semua perhitungan berjalan di browser sehingga data penelitian tidak keluar dari laptop pengguna.

## Operating Context

Dipakai di laptop atau ponsel saat mengolah data skripsi, berdampingan dengan Excel, SPSS, dan Word. Datanya berupa file CSV/Excel hasil rekap kuesioner (sering memakai format Excel Indonesia: pemisah titik koma dan koma desimal). Hasilnya disalin ke naskah skripsi dan dibawa ke bimbingan atau sidang.

## Capabilities and Constraints

- Input: upload CSV/XLSX/XLS, ketik/paste manual (jumlah Y dan X dipilih), atau dataset contoh.
- Penyusunan skor dari item, pembalikan item unfavorable, deteksi salah input dan item yang belum dibalik.
- Enam tujuan analisis: korelasi, regresi, uji-t independen, uji-t berpasangan, ANOVA satu arah, dan cek normalitas saja.
- Tujuh uji normalitas, status hijau/kuning/merah berdasarkan aturan ukuran sampel (bukan voting), grafik histogram, Q-Q, P-P, dan boxplot.
- Diagnosis penyebab dan solusi berurutan berlabel kejujuran; eksklusi outlier wajib disertai alasan.
- Laporan bahasa Indonesia dengan rujukan.
- Data tidak boleh dikirim ke server; tanpa login, tanpa analytics.
- Belum termasuk v1: validitas/reliabilitas, uji asumsi lain, ekspor .docx.
- Istilah: "responden", "item", "skala", "variabel X/Y", "residual", "uji prasyarat", "Bab IV", "dosen penguji".

## Brand Commitments

- Nama: **Normalin**.
- Bahasa Indonesia, menyapa dengan "kamu", nada santai seperti kakak tingkat yang paham statistik dan tidak menggurui.
- Proyek pribadi: footer berisi "dibuat oleh [nama pembuat]" tanpa logo kampus. Nama pembuat belum diberikan, jadi jangan diisi sendiri.

## Evidence on Hand

- Fakta latar (sumber publik): sekitar 8,29 juta mahasiswa S1 aktif (PDDikti via GoodStats, 2024); kajian skripsi S1 yang menemukan hampir semua skripsi yang diteliti punya kesalahan uji statistik; Midway & White (2025) tentang uji normalitas yang keliru diterapkan pada data mentah.
- Mockup tampilan yang disetujui: `mockup/mockup.html`.
- Tidak ada testimoni, jumlah pengguna, atau dukungan institusi. Jangan dikarang.

## Product Principles

1. Jujur secara statistik lebih penting daripada hasil yang diinginkan pengguna.
2. Penjelasan dulu, angka menyusul: ringkasan awam di atas, detail teknis bisa dibuka.
3. Setiap keputusan harus bisa dipertanggungjawabkan: tampilkan alasan dan rujukannya.
4. Data pengguna adalah milik pengguna: tidak ada yang keluar dari browser.
5. Tidak boleh ada jalan buntu: setiap status merah punya langkah berikutnya.

## Accessibility & Inclusion

Target WCAG 2.2 AA: kontras 4,5:1, navigasi keyboard penuh, fokus terlihat, status tidak hanya dibedakan dengan warna, dan `prefers-reduced-motion` dihormati. Harus nyaman dipakai di ponsel kelas menengah dengan koneksi terbatas; muatan awal Pyodide yang besar wajib diberi indikator dan hanya dimuat sekali.
