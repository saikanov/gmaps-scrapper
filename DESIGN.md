# DESIGN.md — Baraquette Internal Tools Design System

Dokumen ini adalah **design lead reference** untuk membangun tools internal Baraquette.
Tujuannya: menjaga konsistensi visual & cara pikir dengan brand Baraquette (lihat website
company-profile sebagai sumber tone), tapi diadaptasi untuk konteks **aplikasi kerja
internal** — padat data, banyak form, tabel, dan dashboard — bukan halaman pemasaran.

> Stack bebas (high-code). Dokumen ini **tidak** mengatur framework/tooling — hanya
> mengatur **bahasa visual**: warna, tipografi, spacing, komponen, dan prinsip desain.
> Semua token sebaiknya diterjemahkan jadi CSS custom properties / design tokens di stack
> apa pun yang dipakai.

---

## 1. Filosofi Desain — "Cara Pikir"

Brand Baraquette = **premium, tegas, gelap, dengan satu aksen emas yang berharga**.
Untuk tools internal, kita pegang DNA itu tapi tunduk pada satu hukum baru: **kejelasan
dan kecepatan kerja di atas drama visual.** Marketing site boleh dramatis; tool internal
harus efisien.

Lima prinsip yang memandu setiap keputusan:

1. **Terstruktur, bukan berlebihan.** Sebelum menambah komponen/warna/efek, tanya: bisakah
   pakai yang sudah ada? Apakah orang lain paham 6 bulan lagi? Kalau ragu — jangan tambah.
   Tool internal hidup lama dan disentuh banyak orang; konsistensi > kreativitas sesaat.

2. **Emas itu langka.** Gold (`#DBB600`) adalah aksen, bukan warna latar. Pakai untuk
   **satu** hal terpenting per layar: primary action, nilai/metric kunci, state aktif.
   Kalau semua emas, tidak ada yang emas.

3. **Hierarki lewat berat & ruang, bukan lewat banyak warna.** Palet sengaja sempit
   (netral + satu aksen). Bedakan elemen dengan font-weight, ukuran, dan whitespace —
   bukan dengan menambah warna baru.

4. **Data dulu, dekorasi belakangan.** Di tool internal, angka/status/tabel adalah bintang
   utama. Border halus, latar netral, dan tipografi rapi membuat data mudah dipindai.
   Hindari bayangan tebal, gradient, atau ilustrasi yang mengalihkan perhatian.

5. **Tenang & dapat diprediksi.** Transisi singkat (180–280ms), motion fungsional (feedback
   aksi, bukan pamer), dan layout yang konsisten antar halaman. Hormati
   `prefers-reduced-motion`.

---

## 2. Warna

Palet dua kelompok: **netral** (struktur) + **emas** (aksen). Jangan hardcode hex di
komponen — daftarkan sebagai token, panggil token-nya.

### 2.1 Brand / Aksen — Gold

| Token | Hex | Pakai untuk |
|---|---|---|
| `--color-gold` | `#DBB600` | Aksen utama: primary button, link aktif, highlight metric, focus ring |
| `--color-gold-deep` | `#B89800` | Hover state dari gold (lebih gelap) |
| `--color-gold-soft` | `#DBB60099` | Gold transparan untuk garis/penekanan halus |
| `--color-gold-tint` | `rgba(219,182,0,0.12)` | Latar pill/badge/highlight bernuansa emas |

> Catatan: `--color-gold-hero` (`#E7C200`) di marketing site khusus judul hero. Di tool
> internal **tidak dipakai** — tidak ada "hero".

### 2.2 Netral — Dark (untuk shell, sidebar, top bar, mode gelap)

| Token | Hex | Pakai untuk |
|---|---|---|
| `--color-bg-dark` | `#0D0D0D` | Latar terdalam: sidebar, top nav, app shell |
| `--color-bg-mid` | `#1A1A1A` | Latar sekunder gelap, footer bar |
| `--color-bg-card` | `#232323` | Kartu/panel di atas latar gelap |
| `--color-bg-panel` | `#292B2B` | Panel "frosted" / box menonjol di area gelap |
| `--color-bg-charcoal` | `#1F2120` | Varian panel lebih gelap (detail/highlight) |

### 2.3 Netral — Light (untuk area kerja utama: tabel, form, konten)

| Token | Hex | Pakai untuk |
|---|---|---|
| `--color-bg-light` | `#FFFFFF` | Latar konten utama, kartu di mode terang |
| `--color-bg-gray` | `#F2F2F2` | Latar halaman / zebra row / area input non-aktif |
| `--color-off-white` | `#FDFDFD` | Permukaan near-white, teks di atas panel gelap |
| `--color-surface-gray` | `#C9C9C9` | Placeholder gambar / skeleton |
| `--color-border` | `#D9D9D9` | Border kartu, divider, garis tabel |

### 2.4 Teks

| Token | Hex | Pakai untuk |
|---|---|---|
| `--color-text` | `#1A1A1A` | Teks utama di latar terang |
| `--color-text-light` | `#FFFFFF` | Teks utama di latar gelap |
| `--color-text-muted` | `#969696` | Teks sekunder, label, caption |
| `--color-text-dim` | `#A0A0A0` | Teks sekunder di latar gelap |

### 2.5 Warna Semantik (status) — **wajib ditambahkan untuk tool internal**

Marketing site tidak butuh ini, tapi tool internal butuh status yang jelas. Pilih hue yang
hidup berdampingan dengan emas (hindari kuning/oranye yang bentrok dengan gold):

| Token | Hex (saran) | Makna |
|---|---|---|
| `--color-success` | `#2E7D5B` | Sukses, aktif, lunas, terkirim |
| `--color-warning` | `#C77D00` | Perlu perhatian, pending (oranye-amber, bukan kuning) |
| `--color-danger` | `#C0392B` | Error, gagal, hapus, overdue |
| `--color-info` | `#2D6CB5` | Informasi netral, draft, in-review |

Setiap status punya 2 turunan: warna teks/icon (di atas) + latar tint 10–12% untuk badge.
Jangan pakai gold sebagai status — gold = aksi/brand, bukan "warning".

### 2.6 Aturan pemakaian warna

- **Mode shell gelap, area kerja terang.** Pola yang paling cocok dengan brand: sidebar +
  top bar gelap (`--color-bg-dark`), area konten terang (`--color-bg-light`/`--color-bg-gray`).
  Ini meneruskan kesan premium brand tanpa melelahkan mata saat baca data seharian.
- **Kontras teks minimum** ikut WCAG AA: ≥ 4.5:1 untuk teks normal, ≥ 3:1 untuk teks besar.
  Gold di atas dark lolos; **gold di atas putih TIDAK** — jangan pakai teks gold di latar
  terang kecuali ukuran besar & tebal.
- **Satu primary action per layar/konteks** berwarna gold solid. Sisanya outline/ghost.

---

## 3. Tipografi

**Satu typeface untuk semuanya: `Plus Jakarta Sans`** (fallback `system-ui, sans-serif`).
Konsistensi font adalah keputusan brand — jangan campur dengan typeface lain.

```
--font-base: 'Plus Jakarta Sans', system-ui, sans-serif;
```

### 3.1 Skala (disesuaikan untuk UI padat)

Marketing site pakai `clamp()` besar untuk hero. Tool internal lebih kecil & stabil —
density penting. Skala saran:

| Token | Ukuran | Pakai untuk |
|---|---|---|
| `--fs-display` | 28px / 700 | Judul halaman utama (jarang) |
| `--fs-h1` | 22px / 700 | Judul section/page |
| `--fs-h2` | 18px / 600 | Sub-judul, judul kartu |
| `--fs-h3` | 16px / 600 | Judul kecil / group label |
| `--fs-body` | 14px / 500 | Teks default UI (body, isi tabel, input) |
| `--fs-small` | 13px / 500 | Caption, helper text, meta |
| `--fs-micro` | 12px / 600 | Label uppercase, badge, tag |

> Catatan density: 14px body adalah default tool internal (vs 16px di marketing site).
> Naikkan ke 16px hanya bila layar memang lapang dan teksnya naratif.

### 3.2 Aturan tipografi

- **Berat font:** 700 = judul/penekanan, 600 = sub-judul & label/tombol, 500 = body default.
  Hindari 400 (terlalu tipis untuk UI) dan 800/900 (terlalu "marketing").
- **Line-height:** 1.15 untuk heading, 1.5–1.6 untuk body/paragraf, 1.3 untuk teks padat
  dalam tabel/badge.
- **Eyebrow / overline label:** `--fs-micro`, weight 600, `letter-spacing: 0.02em`,
  warna `--color-gold` atau `--color-text-muted`. Pakai untuk label kategori/section.
- **Angka di tabel/metric:** pertimbangkan `font-variant-numeric: tabular-nums` agar kolom
  angka rata.

---

## 4. Spacing, Layout & Bentuk

### 4.1 Spacing scale (basis 4px)

Tool internal lebih rapat dari marketing site. Pakai skala 4px:

```
--space-1: 4px;    --space-2: 8px;    --space-3: 12px;   --space-4: 16px;
--space-5: 20px;   --space-6: 24px;   --space-8: 32px;   --space-10: 40px;
--space-12: 48px;  --space-16: 64px;
```

Panduan cepat:
- Gap elemen berdekatan (label↔input, icon↔teks): `--space-2`/`--space-3`.
- Gap antar field dalam satu form / antar baris: `--space-4`/`--space-6`.
- Padding kartu/panel: `--space-6` (24px) desktop, `--space-4` mobile.
- Jarak antar section dalam halaman: `--space-10`/`--space-12`.

### 4.2 Radius

| Token | Nilai | Pakai untuk |
|---|---|---|
| `--radius-sm` | 6px | Tombol, input, badge — **default** UI |
| `--radius-md` | 12px | Kartu, panel, modal |
| `--radius-lg` | 24px | Container besar / kasus khusus |
| `--radius-pill` | 999px | Pill, tag, avatar, toggle |

> Tombol di brand pakai radius kecil (6px) untuk tegas/serius — pertahankan ini sebagai
> default. Pill (999px) dipakai khusus untuk tag/badge, bukan tombol utama.

### 4.3 Border & Shadow

- **Border halus** adalah pemisah utama: `1px solid var(--color-border)` di terang,
  `1px solid rgba(255,255,255,0.08)` di gelap. Brand mengandalkan garis tipis, bukan kotak.
- **Shadow seminimal mungkin.** Hanya untuk elemen yang benar-benar mengambang (dropdown,
  modal, popover, sticky bar). Skala:
  - `--shadow-sm: 0 4px 24px rgba(0,0,0,0.08)` (kartu hover/elevated)
  - `--shadow-md: 0 16px 40px rgba(0,0,0,0.12)` (dropdown/popover)
  - `--shadow-lg: 0 18px 40px rgba(0,0,0,0.45)` (modal di shell gelap)
  Hindari shadow di kartu statis dalam tabel/grid — pakai border saja.

### 4.4 Layout aplikasi

- **App shell:** sidebar kiri (nav, gelap) + top bar (judul/aksi/akun) + area konten
  (terang). Sidebar collapsible di layar sempit.
- **Lebar konten:** beri `max-width` pada konten naratif/form (≈ 720–960px) agar nyaman
  dibaca; tabel/dashboard boleh full-width dengan padding container.
- **Padding container:** ~32px desktop, turun ke 16–20px di mobile.
- **Grid:** pakai grid 12-kolom atau auto-fit cards. Kartu metrik dashboard:
  `repeat(auto-fit, minmax(220px, 1fr))`.

### 4.5 Breakpoints

```
sm: 480px   md: 768px   lg: 1024px   xl: 1200px   2xl: 1280px
```

Pendekatan **mobile-first**, tapi tool internal prioritas desktop (kerja di layar besar).
Pastikan tetap fungsional di tablet; mobile cukup "bisa dipakai", bukan utama.

---

## 5. Komponen Inti

Spesifikasi diturunkan dari brand, diadaptasi untuk tool internal. Pakai konvensi penamaan
konsisten (mis. BEM: `.btn`, `.btn--primary`, `.btn__icon`).

### 5.1 Buttons

Tinggi default tool internal **lebih ringkas** dari marketing site (62px → 40px).

| Variant | Tampilan | Pakai untuk |
|---|---|---|
| `--primary` | bg `--color-gold`, teks `--color-bg-dark`, weight 600 | Aksi utama (1 per konteks) |
| `--secondary` / `--ghost-dark` | transparan, border `--color-border`, teks `--color-text` | Aksi sekunder |
| `--ghost` | transparan, border `rgba(255,255,255,0.25)`, teks terang | Aksi di shell gelap |
| `--danger` | bg/teks turunan `--color-danger` | Hapus/aksi destruktif |
| `--link` | tanpa border/bg, teks gold, underline saat hover | Aksi tersier inline |

Spesifikasi: tinggi `36px` (sm) / `40px` (default) / `48px` (lg); padding-inline 16–24px;
radius `--radius-sm`; gap icon–teks `8–10px`; transisi `--transition-fast`.
Hover primary → `--color-gold-deep`. Sertakan state `:focus-visible` (ring gold), `:disabled`
(opacity 0.5, cursor not-allowed), dan loading (spinner + teks/disabled).

### 5.2 Inputs & Forms

- Tinggi sejajar tombol (40px); border `1px solid --color-border`; radius `--radius-sm`;
  padding-inline 12px; bg `--color-bg-light`.
- **Focus:** border `--color-gold` + ring `0 0 0 3px var(--color-gold-tint)`. Jangan pakai
  outline browser default.
- **Label** di atas field (`--fs-small`, weight 600). **Helper text** `--fs-small` muted.
  **Error:** border + teks `--color-danger`, pesan di bawah field.
- Placeholder `--color-text-muted`. Disabled bg `--color-bg-gray`.
- Komponen wajib: text, textarea, select/dropdown, checkbox, radio, toggle switch (track
  gold saat aktif), date picker, search field (icon di kiri).

### 5.3 Cards / Panels

- Terang: bg `--color-bg-light`, border `--color-border`, radius `--radius-md`, padding
  `--space-6`. Gelap: bg `--color-bg-card`/`--color-bg-panel`, border `rgba(255,255,255,0.08)`.
- Hover lift (opsional, hanya kartu interaktif): `translateY(-4px)` + `--shadow-sm`.
- Struktur: header (judul `--fs-h2` + aksi), body, footer opsional.

### 5.4 Badge / Tag / Pill (status)

- Pill: radius `--radius-pill`, padding `4px 12px`, `--fs-micro` weight 600.
- Status: teks + bg-tint dari warna semantik (mis. success → teks `--color-success`,
  bg `rgba(46,125,91,0.12)`). Brand pill (gold): teks `--color-gold`, bg `--color-gold-tint`.
- Dot indicator opsional (6px lingkaran) di kiri untuk status real-time.

### 5.5 Tabel data (komponen paling penting di tool internal)

- Header: bg `--color-bg-gray`, teks `--color-text-muted`, `--fs-micro` uppercase
  letter-spacing 0.02em, sticky saat scroll.
- Baris: border-bottom `1px solid --color-border`; zebra opsional (`--color-bg-gray` 50%);
  hover row bg `--color-gold-tint` ringan atau `--color-bg-gray`.
- Padding sel `12px 16px`; angka rata kanan + `tabular-nums`; teks rata kiri.
- Sertakan: sort indicator, row selection (checkbox), pagination, empty state, loading
  skeleton, sticky first column bila perlu.
- Aksi baris: icon button di kolom kanan atau menu kebab (⋯).

### 5.6 Navigation (sidebar + top bar)

- **Sidebar** gelap (`--color-bg-dark`), item teks `--color-text-light`/`--fs-body`.
  Item aktif: teks/icon `--color-gold` + indikator (garis kiri 2–3px gold atau bg
  `rgba(255,255,255,0.04)`). Hover: bg `rgba(255,255,255,0.04)`. Mendukung grup & collapse.
- **Top bar** gelap atau terang konsisten: judul halaman / breadcrumb di kiri, search +
  notifikasi + avatar akun di kanan. Tinggi ~64px.
- Logo brand di pojok sidebar (mark + wordmark, uppercase, letter-spacing 0.04em).

### 5.7 Feedback & overlay

- **Toast/notification:** muncul kanan-atas/bawah, border-left 3px warna semantik, auto-dismiss,
  shadow `--shadow-md`.
- **Modal/dialog:** overlay `rgba(13,13,13,0.6)`, panel `--color-bg-light` radius `--radius-md`
  shadow `--shadow-lg`, max-width sesuai isi, fokus terjebak di dalam.
- **Empty state:** ikon/ilustrasi netral + judul + 1 kalimat + 1 primary action.
- **Loading:** skeleton (bg `--color-surface-gray` shimmer) untuk konten; spinner gold untuk
  aksi tombol.
- **Confirmation destruktif** selalu pakai modal dengan tombol `--danger` + tombol batal.

---

## 6. Iconography & Imagery

- **Ikon:** satu set garis (line/stroke) konsisten, `stroke: currentColor`, ketebalan ~1.5–2px,
  ukuran grid 24px (16/20 untuk inline). Pakai SVG inline agar mewarisi warna teks. Hindari
  campur ikon filled & outline dalam satu layar.
- **Avatar:** lingkaran (`--radius-pill`); fallback inisial di atas bg netral/gold-tint.
- **Charts/data-viz:** palet konsisten — gold sebagai seri utama/penekanan, sisanya netral
  abu + warna semantik untuk status. Latar chart bersih, grid line halus (`--color-border`),
  hindari 3D/gradient.
- **Gambar produk** (bila ada): rasio tetap, radius `--radius-md`, placeholder
  `--color-surface-gray`.

---

## 7. Motion

Motion = feedback fungsional, bukan dekorasi.

```
--transition-fast: 180ms ease;   /* hover, focus, toggle */
--transition-base: 280ms ease;   /* panel/dropdown/modal masuk */
```

- Hover tombol: `transform: translateY(-1px)` + perubahan warna (≤180ms).
- Masuk panel/modal: fade + slide kecil (≤280ms), easing halus (`cubic-bezier(0.22,1,0.36,1)`).
- **Reveal-on-scroll** (animasi konten muncul) yang dipakai marketing site **tidak cocok**
  untuk tool internal — data harus langsung tampil. Lewati.
- **Wajib hormati** `prefers-reduced-motion: reduce` → matikan animasi/transition non-esensial.

---

## 8. Aksesibilitas (non-negotiable)

- Kontras teks WCAG AA (4.5:1 normal, 3:1 besar/UI). Cek setiap kombinasi warna baru.
- **Status tidak hanya lewat warna** — selalu tambah ikon/teks/label (untuk buta warna).
- `:focus-visible` jelas di semua elemen interaktif (ring gold + tint), tidak pernah
  `outline: none` tanpa pengganti.
- Target sentuh minimal 40×40px.
- Mendukung navigasi keyboard penuh (tab order logis, fokus terjebak di modal, Esc menutup).
- Form: label terkait input, error diumumkan, helper text terhubung.

---

## 9. Ringkasan Token (siap diterjemahkan ke design tokens stack apa pun)

```css
:root {
  /* === Brand / Gold === */
  --color-gold:       #DBB600;
  --color-gold-deep:  #B89800;
  --color-gold-soft:  #DBB60099;
  --color-gold-tint:  rgba(219,182,0,0.12);

  /* === Neutral dark (shell) === */
  --color-bg-dark:     #0D0D0D;
  --color-bg-mid:      #1A1A1A;
  --color-bg-card:     #232323;
  --color-bg-panel:    #292B2B;
  --color-bg-charcoal: #1F2120;

  /* === Neutral light (workspace) === */
  --color-bg-light:    #FFFFFF;
  --color-bg-gray:     #F2F2F2;
  --color-off-white:   #FDFDFD;
  --color-surface-gray:#C9C9C9;
  --color-border:      #D9D9D9;

  /* === Text === */
  --color-text:        #1A1A1A;
  --color-text-light:  #FFFFFF;
  --color-text-muted:  #969696;
  --color-text-dim:    #A0A0A0;

  /* === Semantic (tool internal) === */
  --color-success: #2E7D5B;
  --color-warning: #C77D00;
  --color-danger:  #C0392B;
  --color-info:    #2D6CB5;

  /* === Typography === */
  --font-base: 'Plus Jakarta Sans', system-ui, sans-serif;
  --fs-display: 28px; --fs-h1: 22px; --fs-h2: 18px; --fs-h3: 16px;
  --fs-body: 14px;    --fs-small: 13px; --fs-micro: 12px;

  /* === Spacing (4px base) === */
  --space-1:4px; --space-2:8px; --space-3:12px; --space-4:16px; --space-5:20px;
  --space-6:24px; --space-8:32px; --space-10:40px; --space-12:48px; --space-16:64px;

  /* === Radius === */
  --radius-sm:6px; --radius-md:12px; --radius-lg:24px; --radius-pill:999px;

  /* === Shadow === */
  --shadow-sm: 0 4px 24px rgba(0,0,0,0.08);
  --shadow-md: 0 16px 40px rgba(0,0,0,0.12);
  --shadow-lg: 0 18px 40px rgba(0,0,0,0.45);

  /* === Motion === */
  --transition-fast: 180ms ease;
  --transition-base: 280ms ease;
}
```

---

## 10. Checklist Design Lead (sebelum approve sebuah layar)

- [ ] Hanya **satu** primary action gold per konteks.
- [ ] Warna hanya dari token; tidak ada hex baru yang di-hardcode.
- [ ] Satu typeface (Plus Jakarta Sans), berat & ukuran dari skala.
- [ ] Spacing mengikuti skala 4px; tidak ada angka ajaib.
- [ ] Status pakai warna semantik + ikon/teks (bukan warna saja, bukan gold).
- [ ] Border halus untuk pemisah; shadow hanya untuk elemen mengambang.
- [ ] Tabel: header sticky, sort, pagination, empty & loading state ada.
- [ ] Semua interaktif punya hover, focus-visible, disabled, loading.
- [ ] Kontras AA lolos; navigasi keyboard jalan; `prefers-reduced-motion` dihormati.
- [ ] Konsisten dengan layar lain (layout, posisi aksi, pola yang sama).
</content>
</invoke>
