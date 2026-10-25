# Desain Website Normalin (sebelumnya "Cek Normalitas")

Tanggal: 2026-10-25 · Status: disetujui (Python, semua analisis di v1). Acuan tampilan: `mockup/mockup.html`

## 1. Maksud dan alasannya

Mahasiswa S1 di Indonesia, terutama mahasiswa psikologi yang datanya dari kuesioner (skala Likert),
sering mengeluh "data saya tidak normal" saat uji prasyarat. Mereka bingung uji mana yang dipakai,
bingung membaca output SPSS, dan sering memilih solusi yang salah (memperkecil sampel, membuang
responden sampai p > 0,05).

Website ini membantu mereka **memahami** kenapa datanya tidak normal dan **memilih langkah yang sah
secara statistik**, dengan bahasa yang bisa dipahami orang awam. Hasilnya harus bisa dipertanggung-
jawabkan di depan dosen penguji.

Posisi produk: **bukan** "alat membuat data jadi normal", tetapi "datamu tidak normal? Ini artinya,
dan ini analisis yang tetap sah."

## 2. Pengguna utama

- Mahasiswa S1 yang sedang mengerjakan Bab IV skripsi, terutama psikologi (kuesioner Likert).
- Kemampuan statistik dasar, terbiasa dengan Excel dan SPSS, takut dengan istilah teknis.
- Datanya biasanya: 30–400 responden, beberapa skala (variabel X dan Y), masing-masing terdiri dari
  10–40 item Likert (1–4, 1–5, atau 1–7), ada item favorable dan unfavorable.
- Analisis yang paling sering: korelasi Pearson, regresi linear (sederhana/berganda), uji-t, ANOVA.

## 3. Tujuan, bukan tujuan, dan yang harus dihindari

**Tujuan (v1)**
1. Input data mudah: upload CSV/Excel, ketik/paste manual (pilih jumlah X dan Y), atau pakai contoh data.
2. Menjalankan **semua** uji normalitas yang umum, dengan kesimpulan yang jujur dan mudah dibaca.
3. Menunjukkan **bagian mana** yang membuat data tidak normal (baris/responden, ekor distribusi, efek
   plafon/lantai, item yang lupa dibalik).
4. Memberi **solusi berurutan** sesuai analisis yang mau dipakai, dan bisa langsung menjalankan solusinya
   (transformasi, uji nonparametrik, bootstrap).
5. Menghasilkan teks interpretasi siap tempel ke Bab IV, lengkap dengan rujukan untuk justifikasi.
6. Data **tidak pernah dikirim ke server**: semua dihitung di browser pengguna.

**Bukan tujuan (v1)**
- Login/akun, menyimpan proyek di server.
- Uji validitas dan reliabilitas (Cronbach's alpha), SEM, analisis faktor, multilevel.
- Chatbot AI, fitur berbayar.
- Aplikasi mobile native (cukup web yang responsif).

**Yang harus dihindari (gagal walaupun "jalan")**
- Website yang membantu memanipulasi data: membuang responden otomatis sampai normal, mengarang data,
  atau menyarankan "ganti uji sampai hasilnya normal".
- Output penuh jargon tanpa penjelasan.
- Kesimpulan "p > 0,05 berarti data valid/bagus" atau voting buta antar-uji.
- Harus instal software atau menunggu lama.

## 4. Alur pengguna (satu halaman, bertahap)

```
[Beranda] → 1. Masukkan data → 2. Atur variabel → 3. Pilih tujuan analisis
          → 4. Hasil normalitas → 5. Kenapa tidak normal? → 6. Solusi → 7. Laporan
```

Setiap langkah punya tombol "Kembali" dan "Lanjut". Pengguna bisa melompat ke langkah yang sudah dilewati.
Setiap istilah teknis punya ikon "(?)" yang membuka penjelasan 1–3 kalimat.

### Langkah 1: Masukkan data
Tiga tab:
- **Upload file**: `.csv`, `.xlsx`, `.xls`. Baris pertama = nama kolom. Kalau file Excel punya
  beberapa sheet, pengguna memilih sheet.
- **Ketik sendiri**: pengguna memilih jumlah variabel Y (1–3) dan X (0–10) serta jumlah baris; muncul
  tabel seperti Excel. Bisa paste langsung dari Excel (Ctrl+V).
- **Pakai contoh**: 2–3 dataset contoh (mis. data kuesioner 150 responden dengan efek plafon dan
  satu item unfavorable yang belum dibalik), supaya pengguna bisa mencoba tanpa data sendiri.

Setelah data masuk: tampilkan pratinjau 10 baris pertama, jumlah baris, jumlah kolom, dan peringatan
(kolom berisi teks, sel kosong, angka dengan koma desimal ala Indonesia "3,5").

### Langkah 2: Atur variabel
- Untuk setiap variabel (Y1, X1, X2, ...), pengguna memilih:
  - **Satu kolom** yang sudah berupa skor, atau
  - **Beberapa kolom item** yang dijumlahkan (atau dirata-rata) menjadi skor total.
- Untuk mode item: pengguna bisa menandai item **unfavorable**; website membalik skornya
  (`skor_baru = min + max − skor_lama`, min/max dideteksi dari data atau diisi pengguna).
- Pemeriksaan otomatis di langkah ini:
  - Nilai di luar rentang Likert (mis. "55" pada skala 1–5) → kemungkinan salah ketik, sorot barisnya.
  - Item dengan korelasi item-total negatif → "Item ini mungkin unfavorable dan belum dibalik."
- Opsional: kolom **kelompok** (mis. jenis kelamin) untuk uji-t/ANOVA.
- Data kosong: baris yang tidak lengkap dikeluarkan (listwise), jumlahnya ditampilkan.

### Langkah 3: Pilih tujuan analisis
Pertanyaan ini menentukan **apa yang sebenarnya harus normal**. Pilihan ditulis dalam bahasa awam:

| Pilihan pengguna | Analisis | Yang dicek normalitasnya |
|---|---|---|
| "Saya mau lihat hubungan dua variabel" | Korelasi Pearson | Tiap variabel (catatan: idealnya normal bivariat) |
| "Saya mau lihat pengaruh X terhadap Y" | Regresi linear | **Residual** model |
| "Saya mau bandingkan 2 kelompok" | Uji-t independen | Tiap kelompok |
| "Saya mau bandingkan sebelum dan sesudah" | Uji-t berpasangan | **Selisih** sebelum−sesudah |
| "Saya mau bandingkan lebih dari 2 kelompok" | ANOVA satu arah | Residual / tiap kelompok |
| "Saya cuma mau cek normalitas" | – | Tiap variabel yang dipilih |

Kalimat penjelas yang selalu tampil: "Untuk regresi, yang harus normal adalah residual, bukan data
mentahnya. Banyak skripsi dan paper keliru di sini."

### Langkah 4: Hasil normalitas
**Ringkasan di atas** (satu kartu per hal yang diuji), dengan tiga status:
- Hijau "Normal / cukup normal"
- Kuning "Sedikit menyimpang, masih aman untuk analisismu" (dengan alasan)
- Merah "Tidak normal, lihat solusi"

**Tabel semua uji** (bisa dibuka/ditutup):

| Uji | Keterangan untuk pengguna |
|---|---|
| Shapiro-Wilk | Paling dianjurkan untuk n kecil–menengah |
| Kolmogorov-Smirnov (Lilliefors) | Versi KS yang benar bila mean/SD diestimasi dari data |
| Kolmogorov-Smirnov klasik (seperti "One-Sample K-S" SPSS) | Ditampilkan karena sering dipakai di skripsi, dengan peringatan bahwa versi ini terlalu longgar |
| Anderson-Darling | Lebih peka terhadap ekor distribusi |
| Jarque-Bera | Berdasarkan skewness dan kurtosis, cocok untuk n besar |
| D'Agostino-Pearson K² | Gabungan skewness dan kurtosis |
| Skewness & kurtosis (nilai dan z) | Ukuran besarnya penyimpangan, bukan sekadar signifikan/tidak |

Setiap baris: statistik uji, p-value, dan kalimat awam ("p = 0,003 < 0,05 → data berbeda nyata dari
distribusi normal").

**Grafik**: histogram + kurva normal, Q-Q plot, P-P plot (yang biasa diminta dosen untuk regresi),
boxplot. Titik yang bermasalah diberi warna berbeda dan bisa diklik untuk melihat barisnya.

**Aturan kesimpulan (status hijau/kuning/merah)** — bukan voting:
1. n < 50: utamakan Shapiro-Wilk.
2. 50 ≤ n ≤ 300: Shapiro-Wilk ditambah z-skewness dan z-kurtosis (batas |z| < 3,29).
3. n > 300: p-value hampir selalu signifikan untuk penyimpangan kecil, jadi gunakan nilai absolut
   skewness (< 2) dan kurtosis berlebih (< 7) serta grafik (Kim, 2013; West dkk., 1995).
4. Kuning bila uji formal menolak normalitas tetapi besarnya penyimpangan kecil dan analisis yang
   dipilih cukup tahan (mis. uji-t dengan n per kelompok ≥ 30).
5. Selalu tampilkan berapa uji yang menolak, tetapi kesimpulan mengikuti aturan di atas.
6. Taraf signifikansi default 0,05, bisa diganti ke 0,01 (keputusan saya).
7. Bila ada lebih dari satu Y pada regresi, tiap Y menjadi model terpisah (keputusan saya).
8. Post-hoc Dunn tidak tersedia di scipy, jadi ditulis sendiri di `stats.py` (koreksi Bonferroni).

### Langkah 5: Kenapa tidak normal?
Daftar temuan, masing-masing dengan penjelasan awam dan baris data yang terkait:
- **Miring ke kanan/kiri** (skewness), beserta kemungkinan penyebab di data kuesioner.
- **Efek plafon/lantai**: banyak responden di skor maksimum/minimum (≥ 15% di nilai ekstrem).
- **Ekor tebal/tipis** (kurtosis).
- **Outlier**: berdasarkan IQR (1,5×) dan |z| > 3; untuk regresi juga residual terstandar > 3,
  Cook's distance > 4/n, dan Mahalanobis (p < 0,001). Disorot per baris, **tidak dihapus otomatis**.
- **Dua puncak (bimodal)**: kemungkinan ada dua subkelompok (mis. laki-laki vs perempuan).
- **Nilai terlalu sedikit variasinya**: skor hanya punya sedikit nilai unik.
- **Salah input / item belum dibalik** (dari langkah 2).

### Langkah 6: Solusi
Ditampilkan **berurutan dari yang paling dianjurkan**. Setiap solusi punya label kejujuran:
"Dianjurkan", "Boleh dengan catatan", atau "Hati-hati".

1. **Apakah kamu memang perlu normal?** (Dianjurkan) — cek apakah yang diuji sudah benar (residual vs
   data mentah), dan apakah n sudah cukup besar sehingga analisis tetap tahan.
2. **Perbaiki salah input / balik item unfavorable** (Dianjurkan) — hanya jika memang kesalahan, lalu uji ulang.
3. **Pakai uji alternatif yang tidak butuh normal** (Dianjurkan), langsung dijalankan:

   | Analisis awal | Alternatif |
   |---|---|
   | Korelasi Pearson | Spearman (atau Kendall tau bila banyak nilai kembar) |
   | Regresi linear | Regresi dengan bootstrap CI / robust standard error (HC3) |
   | Uji-t independen | Mann-Whitney U |
   | Uji-t berpasangan | Wilcoxon signed-rank |
   | ANOVA satu arah | Kruskal-Wallis (+ post-hoc Dunn) |

4. **Transformasi data** (Boleh dengan catatan): log, akar, kebalikan, Box-Cox, Yeo-Johnson. Untuk data
   miring kiri, data direfleksikan dulu. Tampilkan hasil sebelum vs sesudah (grafik + uji ulang) dan
   catatan bahwa interpretasi berubah (yang dianalisis jadi skor hasil transformasi).
5. **Mengeluarkan outlier** (Hati-hati): hanya bila ada alasan yang jelas (salah input, responden tidak
   serius, di luar populasi). Pengguna wajib memilih alasannya; website menampilkan hasil dengan dan
   tanpa outlier berdampingan, dan laporan mencatat berapa yang dikeluarkan dan kenapa.

Yang **tidak** ditawarkan sama sekali: hapus otomatis sampai normal, menambah data, mengecilkan sampel.

### Langkah 7: Laporan
- Paragraf interpretasi bahasa Indonesia siap tempel ke Bab IV (hasil uji normalitas, keputusan, analisis
  yang dipakai, dan alasannya).
- Tabel gaya APA (bisa disalin ke Word).
- Daftar rujukan untuk setiap keputusan (mis. Kim, 2013; Field; Ghasemi & Zahediasl, 2012; Midway &
  White, 2025), supaya mahasiswa bisa mengutipnya.
- Tombol: salin teks, unduh data hasil (CSV, termasuk skor total/transformasi), cetak ke PDF (fitur
  cetak browser).

## 5. Tampilan

- Bahasa Indonesia, nada ramah, kalimat pendek.
- Ringkasan dulu, detail teknis bisa dibuka (progressive disclosure), supaya orang awam tidak kewalahan
  dan mahasiswa statistik tetap bisa melihat angka lengkap.
- Responsif sampai lebar ponsel; tabel lebar bisa digeser.
- Warna status hijau/kuning/merah selalu disertai ikon dan teks (tidak hanya warna).
- Indikator "Data kamu tidak dikirim ke mana pun, semua dihitung di browser" terlihat di langkah 1.

## 6. Cara dibuat (keputusan saya, bisa diganti)

- **Semua berjalan di browser** dengan **Pyodide** (Python di browser): `scipy.stats`, `statsmodels`,
  `pandas`, `openpyxl`. Alasan: data penelitian tidak keluar dari laptop pengguna, tidak perlu server,
  hosting gratis (GitHub Pages/Netlify), dan rumus statistiknya memakai pustaka yang sudah teruji.
  Konsekuensi: muatan awal sekitar 10–20 MB (sekali, lalu di-cache), tampilkan indikator "menyiapkan
  mesin statistik" saat pertama dibuka.
- **Tampilan**: HTML + CSS + JavaScript biasa, tanpa framework dan tanpa build step.
- **Grafik**: Plotly.js (Q-Q plot interaktif dengan titik yang bisa diklik).
- **Struktur berkas**:
  - `index.html` — beranda + 7 langkah
  - `style.css`
  - `app.js` — alur langkah, input tabel, memanggil fungsi Python, menggambar grafik
  - `stats.py` — semua logika statistik (uji, diagnosis, solusi, teks laporan); fungsi murni yang
    menerima angka dan mengembalikan dict, jadi bisa diuji di Python biasa
  - `test_stats.py` — mencocokkan hasil dengan nilai acuan dari R/SPSS untuk dataset contoh
  - `contoh/` — dataset contoh

## 7. Batasan dan kasus tepi

- Shapiro-Wilk: n minimal 3; untuk n > 5000 beri catatan (scipy memberi peringatan p-value tidak akurat).
- Kolom dengan semua nilai sama → tidak bisa diuji, beri pesan jelas.
- Desimal koma ("3,5") dan pemisah titik koma (CSV dari Excel Indonesia) harus terbaca.
- Ukuran file wajar: sampai ~10.000 baris × 200 kolom.
- Box-Cox butuh data positif → geser otomatis (+konstanta) dan catat di laporan, atau pakai Yeo-Johnson.

## 8. Diserahkan ke pembuat

- Detail visual (warna, font, ikon), selama memenuhi bagian 5.
- Teks penjelasan "(?)" per istilah, selama akurat dan ≤ 3 kalimat.
- Isi dataset contoh.
- Cara menyusun kalimat laporan, selama memuat angka, keputusan, dan alasan.

## 9. Rencana tahap berikutnya (bukan v1)

- Uji validitas dan reliabilitas item (sangat relevan untuk mahasiswa psikologi).
- Uji asumsi lain: linearitas, homogenitas (Levene), multikolinearitas (VIF), heteroskedastisitas.
- Halaman "Belajar" berisi artikel singkat tiap uji.
- Ekspor langsung ke `.docx`.
