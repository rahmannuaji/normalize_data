---
version: 1
slug: "web-index-html"
primary_target: "web/index.html"
related_targets: []
---

# Surface brief: web/index.html (Normalin)

Scope: seluruh aplikasi satu halaman, berisi beranda dan wizard 7 langkah. Mode: **Operate** (beranda hanyalah pintu masuk singkat menuju alat, bukan halaman pemasaran).
Audiens & tugas: mahasiswa S1 (terutama psikologi) yang hasil uji prasyaratnya "tidak normal"; tugasnya memasukkan data, memahami status, memilih solusi yang sah, lalu menyalin laporan ke Bab IV.
Konten & bukti: data milik mahasiswa sendiri, atau dataset contoh berlabel "data contoh". Tidak ada testimoni atau angka pengguna.
Batasan: semua berjalan di browser, mobile 375px, WCAG 2.2 AA, bahasa Indonesia dengan sapaan "kamu".
Arah: dipatok oleh mockup yang disetujui pengguna (`mockup/mockup.html`) + `docs/brand-guidelines.md`; tidak ada pengundian arah.
Momen yang diingat: titik merah di Q-Q plot diklik dan langsung menunjukkan "Responden baris 87".
Belum diputuskan: nama pembuat untuk footer.

## Direction contract

THESIS: Normalin terasa seperti meja konsultasi statistik yang tenang. Hasil uji tampil sebagai diagnosis yang bisa ditelusuri sampai ke responden, bukan dinding tabel output SPSS. Yang ditolak: layout default kategori, yaitu dashboard abu-abu berisi tabel p-value dan tombol "Normalize".

OWN-WORLD: latar #F6F7FB, kartu putih bersudut 14px dengan garis #E3E7EF, satu aksen indigo #3B5BDB untuk aksi/fokus/langkah aktif. Pasangan status hijau/kuning/merah selalu berupa teks + latar soft + ikon Lucide. Plus Jakarta Sans dengan angka tabular. Pratinjau laporan memakai Times New Roman seperti halaman skripsi. Stepper bernomor di header. Tanpa emoji, gradien, atau glass.

STORY: mahasiswa memahami bahwa "tidak normal" bukan jalan buntu, percaya bahwa saran Normalin bisa dibela di depan penguji, lalu memasukkan data, membaca status, membuka penyebab, memilih solusi berlabel, dan menyalin laporan.

FIRST VIEWPORT: di desktop, header (logo kiri, pil privasi kanan). Di bawahnya grid 1,2:1: kiri berisi H1 dua baris 44px (baris kedua indigo), satu paragraf, tombol utama "Mulai cek data" dan tombol sekunder "Coba pakai data contoh", serta mikrocopy "Gratis · Tanpa daftar · Semua dihitung di browsermu"; kanan berisi kartu histogram data contoh dengan kurva normal dan ekor kiri merah. Di mobile semuanya satu kolom dengan kartu grafik di bawah tombol.

FORM: wizard bertahap mengikuti mockup yang dipatok pengguna (bukan hasil roll). seed: none (unavailable)

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
