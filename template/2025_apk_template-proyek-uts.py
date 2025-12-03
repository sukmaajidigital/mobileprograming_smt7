import pymysql
import os
import shutil
from flet import *
from datetime import datetime
from threading import Timer

# =========================================================
# 🔹 Koneksi ke Database
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "2025_db_mad_proyek_uts"
    )

# =========================================================
# 🔹 Halaman Utama (Setelah Login)
# =========================================================
def halaman_utama(page: Page, username, hak_akses):
    # panggil koneksi ke database
    buka_koneksi = koneksi_database()
    perintahSQL = buka_koneksi.cursor()
    
    # pastikan bersih sebelum render halaman utama
    page.clean()
    page.title = "📑 Aplikasi CRUD Penjualan (Login Nav MySQL)"
    page.window.height = 700
    page.window.width = 400
    page.padding = 20

    # 🔘 Fungsi Logout
    def logout(val):
        page.clean()
        halaman_login(page)
        page.update()
    
    # 🔘 Fungsi Loading
    def tampil_loading(text = ""):
        page.controls.clear()
        page.add(
            Column(
                [
                    ProgressRing(width = 60, height = 60),
                    Text(text, size = 16, weight = FontWeight.BOLD)
                ],
                alignment = MainAxisAlignment.CENTER,
                horizontal_alignment = CrossAxisAlignment.CENTER,
            )
        )
        page.update()


    # =========================================================
    # 🛒 Halaman Kelola Produk (CRUD)
    # =========================================================
    def buka_kelola_produk():
        tampil_loading("memuat kelola produk 🍵")
        Timer(3, halaman_kelola_produk).start()   # tampilkan halaman produk setelah loading

    def halaman_kelola_produk():
        page.controls.clear()

        # 🔹 Appbar untuk halaman kelola produk dan tombol kembali
        page.add(
                AppBar(
                    leading = Row([
                        IconButton(icon = Icons.ARROW_BACK, tooltip = "Kembali", on_click = lambda e: tampilkan_halaman(3)),
                        Text("Kembali", style = FontWeight.BOLD, size = 16)
                    ],
                    alignment = MainAxisAlignment.START,
                    spacing = 0,
                ),
                bgcolor = Colors.BLUE_300,
            )
        )

        # 🔹 Kolom inputan untuk form entri produk
        inputan_id_produk = TextField(label = "ID Produk", width = 300, visible = False) # inputan id disembunyikan dari tampilan
        inputan_nama_produk = TextField(label = "Nama Produk", width = 300)
        inputan_stok_produk = TextField(label = "Stok Produk", width = 300)
        # buat notif
        notif_produk = Text("")
        def atur_notif_produk():
            notif_produk.value = ""
            page.update()
        def bersihkan_notif_produk():
            Timer(3, atur_notif_produk).start()
            
        # 🔹 Kolom inputan Upload Gambar (bisa dihapus jika tidak diperlukan)
        gambar_preview = Image(src = "", width = 150, height = 150, fit = ImageFit.CONTAIN, visible = False)
        nama_file_unggahan = Text("", size = 12, color = Colors.GREY)

        # Fungsi unggah gambar produk
        def hasil_unggah_gambar(e: FilePickerResultEvent):
            if e.files:
                file = e.files[0]
                asal_file = file.path
                nama_file = file.name
                os.makedirs("gambar_produk", exist_ok = True) # pastikan folder images/produk ada
                tempat_simpan_file = os.path.join("gambar_produk", nama_file) # tentukan path tujuan (misal: images/produk/nama_file.jpg)
                try:
                    shutil.copy(asal_file, tempat_simpan_file) # perintah salin file ke folder penyimpanan
                    gambar_preview.src = tempat_simpan_file # menampilkan preview file dari lokasi simpan
                    gambar_preview.visible = True
                    nama_file_unggahan.value = tempat_simpan_file  # menyimpan path file yang tersimpan ke DB
                    notif_produk.value = f"✅ Gambar berhasil diupload!"
                    notif_produk.color = Colors.GREEN
                except Exception as ex:
                    notif_produk.value = f"❌ Gagal upload gambar: {ex}"
                    notif_produk.color = Colors.RED
                page.update()
                bersihkan_notif_produk()

        file_picker = FilePicker(on_result = hasil_unggah_gambar)
        page.overlay.append(file_picker)

        tombol_upload_gambar = ElevatedButton(
            "📷 Pilih Gambar",
            on_click = lambda e: file_picker.pick_files(allow_multiple = False), bgcolor = Colors.BLUE_400, color = Colors.WHITE
        )   # ... batas inputan Upload Gambar (bisa dihapus jika tidak diperlukan)
        
        # 🔹 Tabel data produk
        tabel_produk = DataTable( # header tabel data produk
            columns = [
                DataColumn(Text("No.")),
                DataColumn(Text("ID Produk")), # tidak harus sama persis dengan nama kolom di tabel database (boleh di custom)
                DataColumn(Text("Nama Produk")),
                DataColumn(Text("Stok")),
                DataColumn(Text("Gambar")),
                DataColumn(Text("Aksi")),
            ],
            rows = [],
            width = 800,
        )

        # 🔹 Fungsi tampil data produk
        def tampil_data_produk():
            perintahSQL.execute("SELECT * FROM produk")
            hasil_data_produk = perintahSQL.fetchall()
            kolom_tabel = [column[0] for column in perintahSQL.description]
            baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil_data_produk]
                
            tabel_produk.rows.clear()
            no_urut = 1
            for row in baris_tabel:
                tombol_ubah_produk = IconButton(icon = Icons.EDIT, tooltip = "Ubah", on_click = isi_form_edit, data = row)
                tombol_hapus_produk = IconButton(icon = Icons.DELETE, tooltip = "Hapus", icon_color = Colors.RED, on_click = hapus_data_produk, data = row)

                # menampilkan gambar kecil
                if row["gambar_produk"] and os.path.exists(row["gambar_produk"]):
                    tampil_gambar = Image(src = row["gambar_produk"], width = 35, height = 35)
                
                # menampilkan teks/ikon jika gambar kosong
                else:
                    tampil_gambar = Text("🖼️", color = Colors.RED, size = 20)

                tabel_produk.rows.append(
                    DataRow( # isi tabel data produk
                        cells = [
                            DataCell(Text(no_urut)),
                            DataCell(Text(row["id_produk"])), # sesuai nama kolom di tabel database
                            DataCell(Text(row["nama_produk"])),
                            DataCell(Text(row["stok_produk"])),
                            DataCell(tampil_gambar),
                            DataCell(Row([tombol_ubah_produk, tombol_hapus_produk])),
                        ]
                    )
                )
                no_urut += 1
            page.update()

        # 🔹 Fungsi simpan data baru
        def simpan_data_produk(val):
            # validasi jika terpilih mode edit data
            if (inputan_id_produk.value != ""):
                notif_produk.value = "⚠️ Kamu dalam mode edit data!"
                notif_produk.color = Colors.RED
                page.update()

            # validasi inputan form penjualan jika belum terisi                
            elif (inputan_nama_produk.value == "" or inputan_stok_produk.value == ""):
                notif_produk.value = "⚠️ Semua kolom harus diisi!"
                notif_produk.color = Colors.RED
                page.update()

            # perintah simpan data baru
            else :
                try:
                    sql = "INSERT INTO produk (nama_produk, stok_produk, gambar_produk) VALUES (%s, %s, %s)"
                    val = (inputan_nama_produk.value, inputan_stok_produk.value, nama_file_unggahan.value)
                    perintahSQL.execute(sql, val)
                    buka_koneksi.commit()
                    notif_produk.value = "✅ Data produk berhasil disimpan!"
                    notif_produk.color = Colors.GREEN
                    tampil_data_produk()
                    page.update()
                    bersihkan_form_produk()
                except Exception as ex:
                    notif_produk.value = f"❌ Gagal menyimpan: {ex}"
                    notif_produk.color = Colors.RED
                    page.update()
                    bersihkan_form_produk()
                    
        # 🔹 Fungsi isi form untuk ubah data
        def isi_form_edit(val):
            inputan_id_produk.value = val.control.data['id_produk'] # sesuai nama kolom di tabel database
            inputan_nama_produk.value = val.control.data['nama_produk']
            inputan_stok_produk.value = val.control.data['stok_produk']
            gambar_preview.src = val.control.data['gambar_produk'] if val.control.data['gambar_produk'] else ""
            nama_file_unggahan.value = val.control.data['gambar_produk'] or ""
            notif_produk.value = "✏️ Mode edit aktif"
            notif_produk.color = Colors.ORANGE
            page.update()

        # 🔹 Fungsi update data
        def update_data_produk(val):
            # validasi jika belum memilih data yang ingin di edit
            if inputan_id_produk.value == "":
                    notif_produk.value = "⚠️ Pilih data yang akan diubah!"
                    notif_produk.color = Colors.RED
                    page.update()

            # perintah simpan perubahan data
            else:
                try:
                    sql = "UPDATE produk SET nama_produk=%s, stok_produk=%s, gambar_produk=%s WHERE id_produk=%s"
                    val = (inputan_nama_produk.value, inputan_stok_produk.value, nama_file_unggahan.value, inputan_id_produk.value)
                    perintahSQL.execute(sql, val)
                    buka_koneksi.commit()
                    notif_produk.value = "✅ Data produk berhasil diperbarui!"
                    notif_produk.color = Colors.GREEN
                    page.update()
                    tampil_data_produk()
                    bersihkan_form_produk()
                except Exception as ex:
                    notif_produk.value = f"❌ Gagal memperbarui: {ex}"
                    notif_produk.color = Colors.RED
                    page.update()
                    bersihkan_form_produk()
                            
        # 🔹 Fungsi hapus data
        def hapus_data_produk(val):
            try:
                perintahSQL.execute("DELETE FROM produk WHERE id_produk=%s", (val.control.data['id_produk'],))
                buka_koneksi.commit()
                notif_produk.value = f"🗑️ Data produk {val.control.data['nama_produk']} berhasil dihapus!"
                notif_produk.color = Colors.GREEN
                page.update()
                tampil_data_produk()
                bersihkan_form_produk()
            except Exception as ex:
                notif_produk.value = f"❌ Gagal menghapus: {ex}"
                notif_produk.color = Colors.RED
                page.update()
                bersihkan_form_produk()
                
        # 🔹 Reset form produk
        def bersihkan_form_produk():
                inputan_id_produk.value = ""
                inputan_nama_produk.value = ""
                inputan_stok_produk.value = ""
                gambar_preview.src = ""
                gambar_preview.visible = False # sembunyikan preview kosong
                nama_file_unggahan.value = ""
                page.update()
                bersihkan_notif_produk()
                
        # 🔹 Layout halaman
        tampil_data_produk()
        page.add(
            Container(
                content = Column(
                    [
                        # bagian form entri
                        Row([Text("📑 Form Entri", size = 16, weight = "bold")], width = 400, alignment = MainAxisAlignment.START),
                        inputan_id_produk,
                        inputan_nama_produk,
                        inputan_stok_produk,
                        tombol_upload_gambar,
                        gambar_preview,
                        nama_file_unggahan,
                        Row(
                            [
                                ElevatedButton("💾 Simpan", on_click = simpan_data_produk, bgcolor = Colors.GREEN, color = Colors.WHITE),
                                ElevatedButton("♻️ Update", on_click = update_data_produk, bgcolor = Colors.ORANGE, color = Colors.WHITE ),
                                ElevatedButton("❌ Batal", on_click = lambda e: bersihkan_form_produk(), bgcolor = Colors.GREY_500, color = Colors.WHITE),
                            ],
                            alignment = MainAxisAlignment.CENTER,
                        ),
                        notif_produk,
                        Divider(),
                        # bagian tabel data
                        Row([Text("📋 Daftar Produk", size = 16, weight = "bold")], width = 400, alignment = MainAxisAlignment.START),
                        Row([tabel_produk], scroll = ScrollMode.ALWAYS, width = 400),
                    ],
                    scroll = ScrollMode.ALWAYS,
                    alignment = MainAxisAlignment.CENTER,
                    horizontal_alignment = CrossAxisAlignment.CENTER,
                ),
                alignment = alignment.top_center,
                expand =True,
            )
        )
        page.update()


    # -------------------------------------------------
    # 🧭 Fungsi Halaman
    # -------------------------------------------------
    def tampilkan_halaman(index):
        # sebelum membuat AppBar, kita clear controls agar tidak duplikasi
        page.controls.clear()

        # Judul dinamis untuk AppBar
        judul = "🏠 Beranda"
        if index == 1:
            judul = "👤 Profil"
        elif index == 2:
            judul = "ℹ️ Tentang"
        elif index == 3:
            judul = "📑 Kelola Penjualan"

        # AppBar dengan tombol Logout
        appbar = AppBar(
            title = Text(f"{judul}", size = 16),
            bgcolor = Colors.BLUE_300,
            center_title = True,
            actions = [
                PopupMenuButton(
                items = [
                    PopupMenuItem(text = f"{username}"),
                    PopupMenuItem(),  # divider
                    PopupMenuItem(
                        text = "↩️ K e l u a r", checked = False, on_click = logout
                    ),
                ]
            ),
        ],
        )

        page.add(appbar)

        # === Isi Halaman ===
        if index == 0:
            page.add(Column([
                Text("🏠 Beranda", size = 24, weight = "bold"),
                Text(f"Selamat datang, {username} ({hak_akses})!", size = 16),
            ]))

        elif index == 1:
            # =========================================================
            # 👤 Halaman Profil - Ubah Username & Password (Tengah)
            # =========================================================
            inputan_username_baru = TextField(label = "Username Baru", width = 300, value = username, read_only = True)
            inputan_password_baru = TextField(label = "Password Baru", password = True, can_reveal_password = True, width = 300)
            notif_profil = Text("")
            def bersihkan_notif():
                notif_profil.value = ""
                page.update()

            def simpan_perubahan(val):
                if inputan_username_baru.value == "" or inputan_password_baru.value == "":
                    notif_profil.value = "⚠️ Username dan Password tidak boleh kosong!"
                    notif_profil.color = Colors.RED
                    page.update()
                    Timer(2, bersihkan_notif).start()
                    return
                
                else :
                    try:
                        sql = "UPDATE user SET username=%s, password=%s WHERE username=%s"
                        perintahSQL.execute(sql, (inputan_username_baru.value, inputan_password_baru.value, username))
                        buka_koneksi.commit()
                        notif_profil.value = "✅ Perubahan berhasil disimpan!"
                        notif_profil.color = Colors.GREEN
                        page.update()
                        Timer(2, bersihkan_notif).start()
                    except Exception as ex:
                        notif_profil.value = f"❌ Gagal menyimpan perubahan: {ex}"
                        notif_profil.color = Colors.RED
                        page.update()
                        Timer(2, bersihkan_notif).start()

            # Gunakan Container + alignment untuk posisi tengah
            page.add(
                Container(
                    content = Column(
                        [
                            Icon(name = Icons.PERSON_OUTLINE_ROUNDED, size = 100),
                            Text(f"Hak Akses: {hak_akses}", size = 16),
                            Divider(),
                            inputan_username_baru,
                            inputan_password_baru,
                            ElevatedButton("💾 Simpan Perubahan", on_click = simpan_perubahan, width = 300, height = 50, color = Colors.WHITE, bgcolor = Colors.BLUE),
                            notif_profil,
                        ],
                        spacing = 15,
                        alignment = MainAxisAlignment.CENTER,
                        horizontal_alignment = CrossAxisAlignment.CENTER,
                    ),
                    alignment = alignment.center,
                    expand = True,
                )
            )


        elif index == 2:
            page.add(Column([
                Text("ℹ️ Tentang Aplikasi", size = 24, weight = "bold"),
                Text("Aplikasi ini dibuat menggunakan Python, Flet, dan MySQL."),
                Text("Contoh sistem login dengan hak akses dan AppBar."),
            ]))

        elif index == 3 and hak_akses == "admin":
            # =========================================================
            # 💰 Form Kelola Penjualan (CRUD Lengkap + Update Stok)
            # =========================================================

            # 🔹 Kolom inputan untuk form entri penjualan
            inputan_id_penjualan = TextField(label = "ID Penjualan", width = 300, visible = False) # inputan id disembunyikan dari tampilan
            inputan_jumlah_penjualan = TextField(label = "Jumlah Penjualan", width = 300)
            # inputan dropdown
            perintahSQL.execute("SELECT * FROM produk ORDER BY id_produk DESC")
            hasil = perintahSQL.fetchall()
            kolom_tabel = [column[0] for column in perintahSQL.description]
            baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil]
            inputan_dropdown_produk = Dropdown(label = "Nama Produk", hint_text = "pilih produk ... ", width = 300,
                options = [
                    dropdown.Option(row["id_produk"], f"{row["nama_produk"]} - stok {row["stok_produk"]}")
                    for row in baris_tabel
                ],
            )
            # buat notif
            notif_penjualan = Text("")
            def atur_notif_penjualan():
                notif_penjualan.value = ""
                page.update()
            def bersihkan_notif_penjualan():
                Timer(3, atur_notif_penjualan).start()

            # 🔹 Tabel data penjualan
            tabel_penjualan = DataTable( # header tabel data penjualan
                columns = [
                    DataColumn(Text("No.")),
                    DataColumn(Text("ID Penjualan")), # tidak harus sama persis dengan nama kolom di tabel database (boleh di custom)
                    DataColumn(Text("Tanggal")),
                    DataColumn(Text("Kode Penjualan")),
                    DataColumn(Text("Produk")),
                    DataColumn(Text("Jumlah")),
                    DataColumn(Text("Aksi")),
                ],
                rows = [],
            )

            # 🔹 Fungsi generate kode penjualan otomatis
            def generate_kode_penjualan():
                waktu = datetime.now().strftime("%d%H%M%S")
                return f"P-{waktu}"

            # 🔹 Fungsi menampilkan data penjualan
            def tampil_data_penjualan():
                perintahSQL.execute("SELECT * FROM penjualan, produk WHERE penjualan.id_produk = produk.id_produk ORDER BY tanggal_penjualan DESC")
                hasil_data_penjualan = perintahSQL.fetchall()
                kolom_tabel = [column[0] for column in perintahSQL.description]
                baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil_data_penjualan]
                tabel_penjualan.rows.clear()
                no_urut = 1

                for row in baris_tabel:
                    tombol_ubah_penjualan = IconButton(icon = Icons.EDIT, tooltip = "Ubah Data", on_click = isi_form_edit, data = row)
                    tombol_hapus_penjualan = IconButton(icon = Icons.DELETE, tooltip = "Hapus Data", icon_color = Colors.RED, on_click = hapus_penjualan, data = row)
                    tabel_penjualan.rows.append(
                        DataRow( # isi tabel data penjualan
                            cells = [
                                DataCell(Text(str(no_urut))),
                                DataCell(Text(row["id_penjualan"])), # sesuai nama kolom tabel di tabel database 
                                DataCell(Text(str(row["tanggal_penjualan"]))),
                                DataCell(Text(row["kode_penjualan"])),
                                DataCell(Text(row["nama_produk"])),
                                DataCell(Text(row["jumlah_penjualan"])),
                                DataCell(Row([tombol_ubah_penjualan, tombol_hapus_penjualan])),
                            ]
                        )
                    )
                    no_urut += 1
                page.update()

            # 🔹 Fungsi simpan data baru + kurangi stok produk
            def simpan_data_penjualan(val):
                # validasi jika terpilih mode edit data
                if (inputan_id_penjualan.value != ""):
                    notif_penjualan.value = "⚠️ Kamu dalam mode edit data!"
                    notif_penjualan.color = Colors.RED
                    page.update()

                # validasi inputan form penjualan jika belum terisi
                elif inputan_jumlah_penjualan.value == "" or inputan_dropdown_produk.value is None:
                    notif_penjualan.value = "⚠️ Semua kolom wajib diisi!"
                    notif_penjualan.color = Colors.RED
                    page.update()
                    
                # validasi dan perintah simpan data baru
                else :
                    # validasi jumlah inputan penjualan (bisa dihapus jika tidak dibutuhkan)
                    try:
                        jumlah = int(inputan_jumlah_penjualan.value)
                        if jumlah <= 0:
                            raise ValueError("Jumlah harus lebih dari 0")
                    except ValueError:
                        notif_penjualan.value = "⚠️ Jumlah penjualan harus angka > 0!"
                        notif_penjualan.color = Colors.RED
                        page.update() 
                        return # ... batas validasi jumlah inputan penjualan (bisa dihapus jika tidak diperlukan)
                    try:
                        # cek stok dulu (bisa dihapus jika tidak dibutuhkan)
                        perintahSQL.execute("SELECT stok_produk FROM produk WHERE id_produk=%s", (inputan_dropdown_produk.value))
                        stok = perintahSQL.fetchone()
                        if not stok or stok[0] < jumlah:
                            notif_penjualan.value = "❌ Stok produk tidak mencukupi!"
                            notif_penjualan.color = Colors.RED
                            page.update() 
                            return # ... batas validasi stok (bisa dihapus jika tidak diperlukan)

                        # simpan penjualan
                        kode_auto_penjualan = generate_kode_penjualan()
                        tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        sql = "INSERT INTO penjualan (tanggal_penjualan, kode_penjualan, jumlah_penjualan, id_produk) VALUES (%s, %s, %s, %s)"
                        val = (tanggal_sekarang, kode_auto_penjualan, jumlah, inputan_dropdown_produk.value)
                        perintahSQL.execute(sql, val)

                        # update stok
                        perintahSQL.execute("UPDATE produk SET stok_produk = stok_produk - %s WHERE id_produk=%s", (jumlah, inputan_dropdown_produk.value))
                        buka_koneksi.commit()
                        
                        notif_penjualan.value = f"✅ Penjualan {kode_auto_penjualan} berhasil disimpan!"
                        notif_penjualan.color = Colors.GREEN
                        tampil_data_penjualan()
                        page.update()
                        bersihkan_form_penjualan()
                    except Exception as ex:
                        notif_penjualan.value = f"❌ Gagal menyimpan: {ex}"
                        notif_penjualan.color = Colors.RED
                        page.update()
                        bersihkan_form_penjualan()

            # 🔹 Isi form untuk ubah data
            def isi_form_edit(val):
                inputan_id_penjualan.value = val.control.data['id_penjualan']
                inputan_jumlah_penjualan.value = str(val.control.data['jumlah_penjualan'])
                inputan_dropdown_produk.value = val.control.data['id_produk']
                notif_penjualan.value = "✏️ Mode edit aktif"
                notif_penjualan.color = Colors.ORANGE
                page.update()

            # 🔹 Update data + sesuaikan stok
            def update_data_penjualan(val):
                # validasi jika belum memilih data yang ingin di edit
                if inputan_id_penjualan.value == "":
                    notif_penjualan.value = "⚠️ Pilih data yang akan diubah!"
                    notif_penjualan.color = Colors.RED
                    page.update()

                # perintah simpan perubahan data
                else:
                    try:
                        # ambil jumlah lama & produk lama (bisa dihapus jika tidak dibutuhkan)
                        perintahSQL.execute("SELECT id_produk, jumlah_penjualan FROM penjualan WHERE id_penjualan=%s", (inputan_id_penjualan.value))
                        lama = perintahSQL.fetchone()
                        if not lama:
                            notif_penjualan.value = "⚠️ Data tidak ditemukan!"
                            notif_penjualan.color = Colors.RED
                            return
                        id_produk_lama, jumlah_lama = lama

                        # kembalikan stok lama
                        perintahSQL.execute("UPDATE produk SET stok_produk = stok_produk + %s WHERE id_produk=%s", (jumlah_lama, id_produk_lama))
                        # kurangi stok baru
                        perintahSQL.execute("UPDATE produk SET stok_produk = stok_produk - %s WHERE id_produk=%s", (inputan_jumlah_penjualan.value, inputan_dropdown_produk.value))
                        # ... batas validasi pembaharuan stok (bisa dihapus jika tidak diperlukan)

                        # update data penjualan
                        sql = "UPDATE penjualan SET jumlah_penjualan=%s, id_produk=%s WHERE id_penjualan=%s"
                        val = (inputan_jumlah_penjualan.value, inputan_dropdown_produk.value, inputan_id_penjualan.value)
                        perintahSQL.execute(sql, val)
                        buka_koneksi.commit()
                        notif_penjualan.value = "✅ Data penjualan berhasil diperbarui!"
                        notif_penjualan.color = Colors.GREEN
                        tampil_data_penjualan()
                        bersihkan_form_penjualan()
                    except Exception as ex:
                        notif_penjualan.value = f"❌ Gagal memperbarui: {ex}"
                        notif_penjualan.color = Colors.RED
                        page.update()
                        bersihkan_form_penjualan()

            # 🔹 Hapus penjualan + kembalikan stok
            def hapus_penjualan(val):
                try:
                    # kembalikan stok
                    perintahSQL.execute("UPDATE produk SET stok_produk = stok_produk + %s WHERE id_produk=%s", (val.control.data['jumlah_penjualan'], val.control.data['id_produk']))
                    perintahSQL.execute("DELETE FROM penjualan WHERE id_penjualan=%s", (val.control.data['id_penjualan'],))
                    buka_koneksi.commit()
                    notif_penjualan.value = f"🗑️ Penjualan {val.control.data['kode_penjualan']} dihapus & stok dikembalikan!"
                    notif_penjualan.color = Colors.GREEN
                    tampil_data_penjualan()
                    bersihkan_form_penjualan()
                except Exception as ex:
                    notif_penjualan.value = f"❌ Gagal menghapus: {ex}"
                    notif_penjualan.color = Colors.RED
                    page.update()
                    bersihkan_form_penjualan()                    

            # 🔹 Reset form penjualan
            def buat_dropdown_produk():
                perintahSQL.execute("SELECT * FROM produk ORDER BY id_produk DESC")
                hasil = perintahSQL.fetchall()
                kolom_tabel = [column[0] for column in perintahSQL.description]
                baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil]
                return Dropdown(label = "Nama Produk", hint_text = "pilih produk ... ", width = 300,
                    options = [
                        dropdown.Option(row["id_produk"], f"{row["nama_produk"]} - stok {row["stok_produk"]}")
                        for row in baris_tabel
                    ],
                )
            def bersihkan_form_penjualan():
                nonlocal inputan_dropdown_produk

                inputan_id_penjualan.value = ""
                inputan_jumlah_penjualan.value = ""

                # Buat dropdown baru
                dropdown_produk_baru = buat_dropdown_produk()
                dropdown_produk_baru.value = None

                # Cari dropdown dalam FORM PENJUALAN → hanya 1 Column saja!
                form_controls = page.controls[1].content.controls  # ← column form
                # (page.controls[0] = AppBar, page.controls[1] = Container(Form))

                # Ganti dropdown lama di list controls
                idx = form_controls.index(inputan_dropdown_produk)
                form_controls[idx] = dropdown_produk_baru

                # Perbarui referensi ke dropdown baru
                inputan_dropdown_produk = dropdown_produk_baru

                page.update()
                bersihkan_notif_penjualan()


            # 🔹 Layout halaman
            tampil_data_penjualan()
            page.add(
                Container(
                    content = Column(
                        [
                            # bagian tombol kelola tabel/data master
                            Row([ 
                                    ElevatedButton("➕ Kelola Produk", on_click = lambda e: buka_kelola_produk(), bgcolor = Colors.GREEN, color = Colors.WHITE)
                                ], alignment = MainAxisAlignment.END
                            ),
                            Divider(),

                            # bagian form entri
                            Row([Text("📑 Form Entri", size = 16, weight = "bold")], width = 400, alignment = MainAxisAlignment.START),
                            inputan_id_penjualan,
                            inputan_jumlah_penjualan,
                            inputan_dropdown_produk,
                            Row(
                                [
                                    ElevatedButton("💾 Simpan", on_click = simpan_data_penjualan, bgcolor = Colors.BLUE, color = Colors.WHITE),
                                    ElevatedButton("♻️ Update", on_click = update_data_penjualan, bgcolor = Colors.ORANGE, color = Colors.WHITE),
                                    ElevatedButton("❌ Batal", on_click = lambda e: bersihkan_form_penjualan(), bgcolor = Colors.GREY_500, color = Colors.WHITE),
                                ],
                                alignment = MainAxisAlignment.CENTER,
                            ),
                            notif_penjualan,
                            Divider(),
                            # bagian tabel data
                            Row([Text("📋 Daftar Penjualan", size = 16, weight = "bold")], width = 400, alignment = MainAxisAlignment.START),
                            Row([tabel_penjualan], scroll = ScrollMode.ALWAYS, width = 400),
                        ],
                        alignment = MainAxisAlignment.START,
                        horizontal_alignment = CrossAxisAlignment.CENTER,
                        scroll = ScrollMode.ALWAYS
                    ),
                    alignment = alignment.top_center,
                    expand = True,
                )
            )

        elif index == 3 and hak_akses == "pemilik":
            # =========================================================
            # 📑 Rekap Transaksi Penjualan (Pemilik) + Pencarian
            # =========================================================

            # 🔍 Input Pencarian
            inputan_cari = TextField(
                label = "🔍 (nama produk / kode / tanggal)",
                width = 300,
                on_change = lambda e: tampil_data_penjualan(),
            )

            # 🔹 Tabel data penjualan
            tabel_penjualan = DataTable(
                columns = [
                    DataColumn(Text("No.")),
                    DataColumn(Text("ID Penjualan")),
                    DataColumn(Text("Tanggal")),
                    DataColumn(Text("Kode Penjualan")),
                    DataColumn(Text("Produk")),
                    DataColumn(Text("Jumlah")),
                ],
                rows = [],
            )

            # 🔹 Fungsi menampilkan data penjualan
            def tampil_data_penjualan():
                keyword = f"%{inputan_cari.value}%" if inputan_cari.value else "%%"

                sql = """ SELECT * FROM penjualan, produk
                    WHERE penjualan.id_produk = produk.id_produk
                    AND (penjualan.kode_penjualan LIKE %s
                        OR produk.nama_produk LIKE %s
                        OR penjualan.tanggal_penjualan LIKE %s
                        OR penjualan.id_penjualan LIKE %s)
                    ORDER BY tanggal_penjualan DESC """

                perintahSQL.execute(sql, (keyword, keyword, keyword, keyword))
                hasil_data_penjualan = perintahSQL.fetchall()
                kolom_tabel = [column[0] for column in perintahSQL.description]
                baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil_data_penjualan]

                tabel_penjualan.rows.clear()
                no_urut = 1

                for row in baris_tabel:
                    tabel_penjualan.rows.append(
                        DataRow(
                            cells = [
                                DataCell(Text(str(no_urut))),
                                DataCell(Text(row["id_penjualan"])),
                                DataCell(Text(str(row["tanggal_penjualan"]))),
                                DataCell(Text(row["kode_penjualan"])),
                                DataCell(Text(row["nama_produk"])),
                                DataCell(Text(row["jumlah_penjualan"])),
                            ]
                        )
                    )
                    no_urut += 1

                page.update()

            # 🔹 Layout halaman
            tampil_data_penjualan()
            page.add(
                Container(
                    content = Column(
                        [
                            Row([Text("📋 Rekap Transaksi Penjualan", size = 16, weight = "bold")],
                                width = 400, alignment = MainAxisAlignment.START),
                            inputan_cari,
                            Divider(),
                            Row([tabel_penjualan], scroll = ScrollMode.ALWAYS, width = 400),
                        ],
                        alignment = MainAxisAlignment.START,
                        horizontal_alignment = CrossAxisAlignment.CENTER,
                        scroll = ScrollMode.ALWAYS
                    ),
                    alignment = alignment.top_center,
                    expand = True,
                )
            )

        # Tambahkan Bottom Navigation
        page.add(menu_bottom_bar)
        page.update()

    # -------------------------------------------------
    # 🔘 Bottom Navigation Bar
    # -------------------------------------------------
    def pilih_menu(val):
        tampilkan_halaman(val.control.selected_index)

    menu_bottom_bar = NavigationBar(
        destinations=[
            NavigationBarDestination(icon = Icons.HOME, label = "Beranda"),
            NavigationBarDestination(icon = Icons.PERSON, label = "Profil"),
            NavigationBarDestination(icon = Icons.INFO, label = "Tentang"),
            NavigationBarDestination(icon = Icons.NOTE, label = "Penjualan"),
        ],
        on_change = pilih_menu,
        selected_index = 0,
    )

    tampilkan_halaman(0) # menampilkan secara default halaman ketika aplikasi pertama kali di jalankan

# =========================================================
# 🔹 Halaman Login
# =========================================================
def halaman_login(page: Page):
    # sangat penting: bersihkan halaman dulu agar AppBar/BottomNav sebelumnya hilang
    page.clean()
    page.title = "🔐 Login Aplikasi UTS"
    page.window.height = 700
    page.window.width = 400
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER

    # 🔘 Fungsi Loading
    def tampil_loading(text = ""):
        page.clean()
        page.add(
            Column(
                [
                    ProgressRing(width = 60, height = 60),
                    Text(text, size = 16, weight = FontWeight.BOLD)
                ],
                alignment = MainAxisAlignment.CENTER,
                horizontal_alignment = CrossAxisAlignment.CENTER,
            )
        )
        page.update()

    # 🔹 Kolom inputan untuk form login
    inputan_username = TextField(label = "Username", width = 250)
    inputan_password = TextField(label = "Password", password = True, can_reveal_password = True, width = 250)
    notif_login = Text("", color = Colors.RED)

    # fungsi proses login
    def proses_login(val):
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()
        perintahSQL.execute("SELECT id_user, username, password, hak_akses FROM user WHERE username=%s AND password=%s",
                    (inputan_username.value, inputan_password.value))
        user = perintahSQL.fetchone()

        # validasi jika user ada 
        if user:
            v_id_user, v_username, v_password, v_hak_akses = user
            # update data akses terakhir user
            perintahSQL.execute("UPDATE user SET akses_terakhir=%s WHERE id_user=%s", (datetime.now(), v_id_user))
            buka_koneksi.commit()
            perintahSQL.close()
            buka_koneksi.close()
            # setelah login sukses, panggil halaman utama
            tampil_loading("memuat halaman utama 🍵")
            # Delay agar loading terlihat, lalu masuk ke halaman utama
            Timer(1, lambda: halaman_utama(page, v_username, v_hak_akses)).start()
        
        # validasi jika user tidak ada
        else:
            notif_login.value = "❌ Username atau password salah!"
            page.update()
            def bersihkan_notif():
                notif_login.value = ""
                page.update()
            # Hilangkan notifikasi otomatis setelah 2 detik
            Timer(2, bersihkan_notif).start()

    tombol_login = ElevatedButton("🔓 Login", on_click = proses_login, width = 250, height = 50, bgcolor = Colors.BLUE, color = Colors.WHITE)

    # pastikan kita menambahkan konten setelah page.clean()
    page.add(
        Column(
            [
                Text("📑 Aplikasi CRUD (UTS)", size = 24, weight = "bold"),
                inputan_username, inputan_password,
                tombol_login, notif_login
            ],
            alignment = MainAxisAlignment.CENTER,
            horizontal_alignment = CrossAxisAlignment.CENTER,
        )
    )
    page.update()

# =========================================================
# 🚀 Jalankan Aplikasi
# =========================================================
app(target = halaman_login)
