# Brand Guidelines v1.0 — Normalin

> Last updated: 2026-10-25
> Status: Draft (diturunkan dari mockup yang disetujui, `mockup/mockup.html`)

## Quick Reference

| Element | Value |
|---------|-------|
| Name | Normalin |
| Tagline | Datamu tidak normal? Tenang, ada jalannya. |
| Primary Color | #3B5BDB |
| Secondary Color | #1B2333 |
| Primary Font | Plus Jakarta Sans |
| Voice | Santai, jujur, menenangkan |

---

## 1. Color Palette

Strategi: **Restrained**. Latar netral kebiruan, satu aksen indigo untuk aksi dan fokus. Warna status hanya untuk status, bukan dekorasi. Hanya mode terang. Alasannya: mahasiswa memakai Normalin berdampingan dengan Word, Excel, dan SPSS yang berlatar terang, dan hasilnya dicetak atau ditempel ke naskah putih.

### Primary Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Indigo | #3B5BDB | rgb(59,91,219) | Tombol utama, langkah aktif, tautan, fokus |
| Indigo Dark | #2F49B0 | rgb(47,73,176) | Hover/pressed tombol utama |
| Indigo Soft | #E8EDFF | rgb(232,237,255) | Latar langkah aktif, pilihan terpilih, catatan info |

### Neutral Palette

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Background | #F6F7FB | rgb(246,247,251) | Latar halaman |
| Surface | #FFFFFF | rgb(255,255,255) | Kartu, tabel, header |
| Surface Sunken | #F3F5FA | rgb(243,245,250) | Header tabel, area drop |
| Text Primary | #1B2333 | rgb(27,35,51) | Judul, teks utama |
| Text Secondary | #5D6779 | rgb(93,103,121) | Keterangan, label |
| Border | #E3E7EF | rgb(227,231,239) | Garis kartu dan tabel |

### Semantic Colors

Setiap status selalu memakai pasangan warna teks + latar, ikon, dan label teks.

| State | Hex | Soft | Usage |
|-------|-----|------|-------|
| Success / Normal | #22702F | #E6F6EA | Status hijau, label "Dianjurkan" |
| Warning / Sedikit menyimpang | #8A5200 | #FFF4DD | Status kuning, label "Boleh dengan catatan" |
| Error / Tidak normal | #C92A2A | #FDE8E8 | Status merah, label "Hati-hati", baris bermasalah |
| Info | #24398F | #E8EDFF | Catatan "Tahukah kamu?", penjelasan |

### Accessibility

- Text Primary di Background: 14,7:1. Text Secondary di Surface: 5,7:1 (di Surface Sunken 5,2:1).
- Indigo di putih: 5,7:1 (AA untuk teks normal); teks putih di Indigo juga 5,7:1; Indigo di Indigo Soft: 4,85:1.
- Semua warna status sudah digelapkan agar teksnya ≥ 4,5:1 di atas latar soft masing-masing (hijau 5,5; kuning 5,9; merah 4,65; info 8,8).
- Status tidak boleh hanya dibedakan dengan warna.

---

## 2. Typography

### Font Stack

```css
--font-heading: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
--font-body: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
--font-report: 'Times New Roman', Times, serif;
--font-mono: ui-monospace, 'Cascadia Mono', Consolas, monospace;
```

- Plus Jakarta Sans dipertahankan dari mockup yang disetujui pengguna. Font ini karya foundry Jakarta (Tokotype) dan dipakai untuk audiens Indonesia.
- Angka statistik di tabel dan kartu memakai `font-variant-numeric: tabular-nums` supaya digit sejajar.
- `--font-report` khusus pratinjau laporan Bab IV, supaya terlihat seperti halaman skripsi (Times New Roman, spasi 1,5).

### Type Scale

| Element | Size (Desktop) | Size (Mobile) | Weight | Line Height |
|---------|----------------|---------------|--------|-------------|
| H1 (beranda) | 44px | 30px | 800 | 1.15 |
| H2 (judul langkah) | 24px | 22px | 700 | 1.25 |
| H3 (judul kartu) | 16px | 16px | 700 | 1.35 |
| Body | 16px | 16px | 400 | 1.55 |
| Small | 14px | 14px | 400 | 1.5 |
| Caption / label | 13px | 13px | 500–600 | 1.4 |
| Laporan | 16px | 15px | 400 | 1.7 |

Tidak ada teks di bawah 12px.

### Font Loading

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

---

## 3. Logo Usage

Logo: **tanda kurva lonceng** (satu garis kurva normal di dalam kotak indigo bersudut 8px) + wordmark **"Normalin"** (Plus Jakarta Sans 800, tracking −0,02em, warna Text Primary).

### Variants

| Variant | File | Use Case |
|---------|------|----------|
| Full Horizontal | web/assets/logo.svg | Header |
| Icon Only | web/assets/favicon.svg | Favicon, ruang sempit |

### Clear Space

Ruang kosong minimal = tinggi tanda.

### Minimum Size

| Context | Minimum Width |
|---------|---------------|
| Digital - Full Logo | 112px |
| Digital - Icon | 20px |

### Don'ts

- Jangan memutar, memiringkan, atau memberi bayangan.
- Jangan memakai warna di luar palet.
- Jangan mengganti kurva dengan ikon lain (grafik batang, centang, dsb.).

---

## 4. Voice & Tone

### Brand Personality

| Trait | Description |
|-------|-------------|
| **Menenangkan** | Mahasiswa datang dalam keadaan panik; kalimat pertama meredakan, bukan menghakimi |
| **Jujur** | Tidak pernah menjanjikan "data pasti normal"; jelas soal apa yang sah dan tidak |
| **Jelas** | Istilah teknis selalu disertai arti awam |
| **Setara** | Seperti kakak tingkat yang paham statistik, memakai "kamu" |

### Voice Chart

| Trait | We Are | We Are Not |
|-------|--------|------------|
| Menenangkan | "Tenang, ini sering terjadi." | Menggurui ("Kamu salah memakai uji.") |
| Jujur | "Cara ini sah, tapi interpretasinya berubah." | Menjual ("Data langsung normal!") |
| Jelas | "Residual = selisih nilai asli dengan prediksi." | Penuh jargon tanpa arti |
| Setara | "kamu", kalimat pendek | Kaku ("Pengguna dimohon…"), atau alay/berlebihan |

### Tone by Context

| Context | Tone | Example |
|---------|------|---------|
| Beranda | Hangat, langsung ke inti | "Datamu tidak normal? Tenang, ada jalannya." |
| Penjelasan uji | Instruktif, singkat | "Kalau normal, titik mengikuti garis." |
| Status merah | Tenang, langsung ke langkah berikutnya | "Tidak normal. Lihat penyebabnya →" |
| Error | Menjelaskan + solusi | "Uji-t independen butuh tepat 2 kelompok (sekarang 3)." |
| Peringatan etika | Tegas, tanpa menghakimi | "Kami tidak menyediakan hapus otomatis sampai normal." |
| Sukses | Singkat | "Tersalin." |

### Prohibited Terms

| Avoid | Reason |
|-------|--------|
| "Membuat data normal", "menormalkan data" | Bertentangan dengan posisi produk |
| "Data valid" (sebagai arti p > 0,05) | Salah secara statistik |
| "Seamless", "revolusioner", "canggih" | Klaim kosong |
| "Dijamin lulus sidang" | Janji yang tidak bisa ditepati |
| "User", "submit" | Pakai "kamu", "kirim/jalankan" |

---

## 5. Imagery Guidelines

### Photography Style

Tidak memakai foto. Visual utama adalah data mahasiswa itu sendiri: histogram, Q-Q plot, dan tabel.

### Illustrations

- Tidak ada ilustrasi dekoratif. Grafik di beranda memakai data contoh yang diberi label "data contoh".
- Grafik: batang Indigo 55% opacity, kurva normal Text Primary 2px, titik bermasalah Error.

### Icons

- Set: Lucide (lisensi ISC), disalin sebagai `<symbol>` ke `web/assets/icons.svg`.
- Gaya outline, grid 24px, stroke 2px, `currentColor`.
- **Emoji tidak boleh dipakai sebagai ikon.**
- Ikon dekoratif diberi `aria-hidden="true"`; tombol yang hanya berisi ikon wajib punya `aria-label`.

---

## 6. Design Components

### Buttons

| Type | Background | Text | Border Radius |
|------|------------|------|---------------|
| Primary | #3B5BDB | #FFFFFF | 10px |
| Secondary | #FFFFFF + border #E3E7EF | #1B2333 | 10px |
| Small | sama dengan di atas, padding 6×12 | | 10px |

Tinggi minimal target sentuh 44px (tombol kecil tetap punya area sentuh 44px). Fokus: outline 2px Indigo, offset 2px.

### Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Jarak ikon–teks rapat |
| sm | 8px | Jarak di dalam komponen |
| md | 16px | Padding kartu kecil, jarak antarkartu |
| lg | 24px | Padding kartu, jarak antarbagian |
| xl | 32px | Jarak antarbagian besar |
| 2xl | 48px | Jarak bagian di beranda |

### Border Radius

| Element | Radius |
|---------|--------|
| Buttons | 10px |
| Cards | 14px |
| Inputs | 10px |
| Notes | 10px |
| Pills/Tags | 9999px |

### Motion

- Pergantian langkah: fade + geser 6px, 250ms ease-out.
- Hover/fokus: 150–200ms.
- `prefers-reduced-motion: reduce` → semua transisi dimatikan.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-10-25 | Panduan awal dari mockup yang disetujui; nama Normalin; ikon Lucide menggantikan emoji |
