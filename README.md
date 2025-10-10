# **Dual Dimension: Game Design Document**

## **1. Deskripsi Singkat**

**Dual Dimension** adalah game platformer 2D di mana pemain harus melewati level yang penuh dengan jebakan tak terduga. **Pemain mengandalkan kemampuan unik untuk beralih antara dua dimensi**. **Tujuannya adalah untuk menghindari bahaya dan lolos dari setiap level**.

## **2. Gameplay Utama**

### **Tujuan**

**Tujuan utama pemain adalah untuk bertahan hidup dan mencapai pintu keluar di setiap akhir level**. **Pemain harus menggunakan ingatan mereka untuk mengatasi setiap rintangan**. **Jika semua nyawa (heart) habis, progres di level saat itu akan direset total**.

### **Narasi**

**Karakter utama dalam "Dual Dimension" masuk ke realitas yang tidak stabil di antara dunia nyata dan "dimensi gema" yang berbahaya**. **Untuk melarikan diri, ia harus menguasai kemampuannya untuk berpindah antara kedua dimensi ini**. **Platform yang kokoh di satu dimensi bisa menjadi jebakan mematikan di dimensi lainnya**. **Satu-satunya cara untuk maju adalah dengan mencapai pintu-pintu yang ditemukan di setiap level**.

## **3. Alur Game**

**Alur game dirancang untuk memperkenalkan mekanika secara bertahap dengan tantangan yang terus meningkat**.

**Menu Utama** -> **Gameplay Utama** -> **End Game** 

### **a. Menu Utama**

**Tampilan awal saat game dibuka berisi pilihan "Mulai" dan "Keluar"**.

### **b. Gameplay Utama**

**Pemain memulai dari Level 1**. **Setiap kali pemain berhasil mencapai pintu, mereka akan pindah ke level selanjutnya**. **Api unggun berfungsi sebagai *checkpoint*.

* Jika pemain kehilangan satu nyawa, mereka akan kembali ke *checkpoint* terakhir.
* **Jika semua nyawa habis, pemain akan mengalami Game Over dan harus mengulang dari level 1**.

### **c. End Game**

**Saat level terakhir selesai, layar akan menampilkan pilihan "Restart" dan "Main Menu"**.

* **Restart** **: Mengulang permainan dari level 1**.
* **Main Menu** **: Kembali ke layar menu utama**.

### **d. Pause**

Ketika game di-pause, akan ada empat tombol:

* **Lanjutkan** **: Untuk melanjutkan permainan**.
* **Ulangi** : Untuk mengulang permainan ke titik *checkpoint* terakhir.
* **Pengaturan** **: Untuk mematikan atau menyalakan musik**.
* **Menu Utama** **: Untuk kembali ke layar menu utama**.

---

## **4. Mekanika Game**

**Ini adalah daftar interaksi yang bisa dilakukan oleh pemain**.

### **a. Gerakan Dasar**

**Pemain bisa bergerak ke kiri dan kanan menggunakan tombol W dan D atau panah kiri dan panah kanan**. **Lompat bisa dilakukan dengan menekan tombol spasi**.

### **b. Sistem Nyawa ( *Health* )**

**Pemain memulai setiap level dengan 5 nyawa**.

* Terkena jebakan atau musuh akan mengurangi 1 nyawa dan mengembalikan pemain ke ***checkpoint* terakhir**.
* **Jika semua nyawa habis, pemain akan mengalami Game Over dan harus mengulang dari level 1**.

### **c. Pergeseran Dimensi**

**Ini adalah mekanika inti dari game**. Pemain dapat langsung beralih antara Dimensi Normal dan Dimensi Gema dengan menekan tombol . **Pergeseran ini dapat dilakukan kapan saja, baik di darat maupun di udara**.

* **Dimensi Normal** **: Tampilan dunia yang cerah**.
* **Dimensi Gema** **: Tampilan dunia yang gelap**.

### **d. Objek dalam Game**

**Jebakan utamanya berupa duri yang hanya akan mengurangi nyawa pemain**.

## **5. Sistem Progres**

**Progres pemain didorong oleh keberhasilan melewati rintangan**.

* **Progres Berbasis Level** adalah **Kemajuan pemain ditandai dengan level yang berhasil dicapai**.
* **Penyelesaian Level** adalah **Menyelesaikan sebuah level akan memberikan akses ke level berikutnya, yang berisi jebakan dan teka-teki yang lebih kompleks**.
