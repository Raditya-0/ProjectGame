Desain Level SOP (Simbol Peta ASCII)

Ukuran tile: 40 px. Gunakan teks mono-spaced. Setiap karakter mewakili satu tile.
Aturan huruf besar/kecil untuk arah hadap: Huruf besar = hadap kanan, huruf kecil = hadap kiri (untuk musuh).

1) Medan (Terrain)

- G/g  : Tanah (40x40). Menggunakan Assets/Tiles/ground.png. Solid (tidak bisa a).
- P/p  : platform (40x20). Menggunakan Assets/Tiles/platform.png. Solid (bukan platform satu arah).

2) Rintangan (Duri)

- j/J  : Tile duri (jebakan). Beranimasi saat terpicu. Letakkan duri di posisi tile tanah.
- T/t  : Tile pemicu untuk duri. WAJIB. Letakkan tepat satu tile DI ATAS j yang sesuai.
  Area pemicu seukuran tile; saat pemain menyentuhnya, duri akan beranimasi.
  Panduan desain: jaga agar T sejajar secara vertikal dengan j-nya (pasangan satu-ke-satu).

3) Mulai dan Akhir Level

- S/s  : Start point pemain -> Pemain muncul di lokasi S ditaruh
- D    : Pemicu Next Level (jump_walk). Saat disentuh, pemain otomatis melompat sekali lalu berjalan keluar dari kamera; lanjut ke level berikutnya.
- d    : Pemicu akhir (walk). Saat disentuh, pemain berjalan keluar dari kamera; lanjut ke level berikutnya.

4) Musuh

- H/h  : Titik muncul musuh patroli. Arah hadap berdasarkan huruf (H→kanan, h→kiri).
  Batas patroli diatur oleh penanda l/r pada BARIS YANG SAMA (lihat Penanda). Jika tidak ada, defaultnya ±80 px dari titik muncul.
- F/f  : Titik muncul musuh pengejar (Light Bandit). Arah hadap berdasarkan huruf (F→kanan, f→kiri).
  Perilaku: menunggu diam, lalu mengejar pemain saat terdeteksi. Deteksi berdasarkan kedekatan (~140 px horizontal,
  ~80 px vertikal di atas) atau saat pemain melompati pengejar. Setelah waspada, ia akan mengejar secara horizontal.
- N/n  : Titik muncul musuh pengejar berat (Heavy Bandit). Arah hadap: N→kanan, n→kiri.
  Perilaku mirip Light tetapi animasi/skin berbeda.

5) Penanda & Kamera

- l/L  : Penanda batas patroli kiri (gunakan pada baris yang sama dengan titik muncul H/h). Penanda terdekat ≤ x spawn menjadi batas kiri.
- r/R  : Penanda batas patroli kanan (baris yang sama). Penanda terdekat ≥ x spawn menjadi batas kanan.
- K    : Batas kanan kamera opsional (upper-case saja). Kamera tidak bergulir lebih jauh ke kanan dari tengah tile ini.
  Catatan: huruf k kecil tidak digunakan.

6) Api Unggun & Dekorasi

- C/c  : Api unggun (beranimasi). Murni visual; ditempatkan pada tile di mana ia harus dirender.

7) Peta Multi-dimensi (Normal & Gema)

- Peta normal dan gema keduanya di-parse. Titik muncul musuh dari keduanya digabungkan dan duplikat berdasarkan tile dihilangkan.
  Anda dapat menempatkan titik muncul di salah satu peta; duplikat pada tile yang sama diabaikan.
- Tanah/Platform/Rintangan/Pemicu mengikuti aturan yang sama di kedua peta.

Tips Desain

- Untuk setiap duri j, letakkan T yang cocok tepat di atasnya untuk memastikan aktivasi. Jaga agar jumlahnya selaras (satu T per j).
- Untuk musuh patroli (H/h), letakkan penanda l ... r pada baris yang sama untuk menentukan jangkauan jalan.
- Gunakan huruf besar jika Anda ingin musuh menghadap ke kanan pada awalnya; huruf kecil untuk menghadap ke kiri.
- Pemicu akhir (D/d) biasanya ditempatkan di dekat tepi paling kanan. Mereka mengunci input dan kamera serta menggerakkan pemain keluar secara otomatis.
- Buat baris tidak lebih panjang dari yang dibutuhkan; spasi di akhir tidak apa-apa dan diabaikan.
