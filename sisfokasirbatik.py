from flet import *
import pymysql
from datetime import datetime
from threading import Timer

# =========================================================
# 🔹 Koneksi ke Database
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="mobileprograming"
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
    page.title = "🛍️ Sistem Informasi Kasir Batik"
    page.window.height = 700
    page.window.width = 400
    page.padding = 20

    # 🔹 Variabel untuk menyimpan halaman sebelumnya
    halaman_sebelumnya = {"index": 0}  # Default beranda

    # 🔘 Fungsi Logout
    def logout(val):
        page.clean()
        halaman_login(page)
        page.update()
    
    # 🔘 Fungsi Loading
    def tampil_loading(text=""):
        page.controls.clear()
        page.add(
            Column(
                [
                    ProgressRing(width=60, height=60),
                    Text(text, size=16, weight=FontWeight.BOLD)
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
            )
        )
        page.update()

    # =========================================================
    # 🛒 Halaman Kelola Produk (CRUD)
    # =========================================================
    def buka_kelola_produk():
        tampil_loading("Memuat kelola produk 🛍️")
        Timer(1, halaman_kelola_produk).start()

    def halaman_kelola_produk():
        page.controls.clear()

        # 🔹 Appbar untuk halaman kelola produk dan tombol kembali
        page.add(
            AppBar(
                leading=Row([
                    IconButton(icon=Icons.ARROW_BACK, tooltip="Kembali", on_click=lambda e: tampilkan_halaman(halaman_sebelumnya["index"])),
                    Text("Kembali", style=FontWeight.BOLD, size=16)
                ],
                alignment=MainAxisAlignment.START,
                spacing=0,
                ),
                bgcolor=Colors.BLUE_300,
            )
        )

        # 🔹 Kolom inputan untuk form entri produk
        inputan_id_produk = TextField(label="ID Produk", width=300, visible=False)
        inputan_kode_produk = TextField(label="Kode Produk", width=300)
        inputan_nama_produk = TextField(label="Nama Produk", width=300)
        inputan_jenis_batik = Dropdown(
            label="Jenis Batik",
            width=300,
            options=[
                dropdown.Option("Tulis"),
                dropdown.Option("Cap"),
                dropdown.Option("Printing"),
                dropdown.Option("Kombinasi"),
            ]
        )
        inputan_ukuran = Dropdown(
            label="Ukuran",
            width=300,
            options=[
                dropdown.Option("S"),
                dropdown.Option("M"),
                dropdown.Option("L"),
                dropdown.Option("XL"),
                dropdown.Option("XXL"),
            ]
        )
        inputan_harga = TextField(label="Harga", width=300, keyboard_type=KeyboardType.NUMBER)
        inputan_stok = TextField(label="Stok", width=300, keyboard_type=KeyboardType.NUMBER)
        
        # buat notif
        notif_produk = Text("")
        def atur_notif_produk():
            notif_produk.value = ""
            page.update()
        def bersihkan_notif_produk():
            Timer(3, atur_notif_produk).start()
        
        # 🔹 Tabel data produk
        tabel_produk = DataTable(
            columns=[
                DataColumn(Text("No.")),
                DataColumn(Text("Kode")),
                DataColumn(Text("Nama Produk")),
                DataColumn(Text("Jenis")),
                DataColumn(Text("Ukuran")),
                DataColumn(Text("Harga")),
                DataColumn(Text("Stok")),
                DataColumn(Text("Aksi")),
            ],
            rows=[],
            width=800,
        )

        # 🔹 Fungsi tampil data produk
        def tampil_data_produk():
            perintahSQL.execute("SELECT * FROM produk ORDER BY id_produk DESC")
            hasil_data_produk = perintahSQL.fetchall()
            kolom_tabel = [column[0] for column in perintahSQL.description]
            baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil_data_produk]
                
            tabel_produk.rows.clear()
            no_urut = 1
            for row in baris_tabel:
                tombol_ubah_produk = IconButton(icon=Icons.EDIT, tooltip="Ubah", on_click=isi_form_edit, data=row)
                tombol_hapus_produk = IconButton(icon=Icons.DELETE, tooltip="Hapus", icon_color=Colors.RED, on_click=hapus_data_produk, data=row)

                tabel_produk.rows.append(
                    DataRow(
                        cells=[
                            DataCell(Text(no_urut)),
                            DataCell(Text(row["kode_produk"])),
                            DataCell(Text(row["nama_produk"])),
                            DataCell(Text(row["jenis_batik"])),
                            DataCell(Text(row["ukuran"])),
                            DataCell(Text(f"Rp {row['harga']:,.0f}")),
                            DataCell(Text(row["stok"])),
                            DataCell(Row([tombol_ubah_produk, tombol_hapus_produk])),
                        ]
                    )
                )
                no_urut += 1
            page.update()

        # 🔹 Fungsi simpan data baru
        def simpan_data_produk(val):
            if (inputan_id_produk.value != ""):
                notif_produk.value = "⚠️ Kamu dalam mode edit data!"
                notif_produk.color = Colors.RED
                page.update()
            elif (inputan_kode_produk.value == "" or inputan_nama_produk.value == "" or 
                  inputan_jenis_batik.value is None or inputan_ukuran.value is None or
                  inputan_harga.value == "" or inputan_stok.value == ""):
                notif_produk.value = "⚠️ Semua kolom harus diisi!"
                notif_produk.color = Colors.RED
                page.update()
            else:
                try:
                    sql = "INSERT INTO produk (kode_produk, nama_produk, jenis_batik, ukuran, harga, stok) VALUES (%s, %s, %s, %s, %s, %s)"
                    val = (inputan_kode_produk.value, inputan_nama_produk.value, inputan_jenis_batik.value, 
                           inputan_ukuran.value, inputan_harga.value, inputan_stok.value)
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
                    
        # 🔹 Fungsi isi form untuk ubah data
        def isi_form_edit(val):
            inputan_id_produk.value = val.control.data['id_produk']
            inputan_kode_produk.value = val.control.data['kode_produk']
            inputan_nama_produk.value = val.control.data['nama_produk']
            inputan_jenis_batik.value = val.control.data['jenis_batik']
            inputan_ukuran.value = val.control.data['ukuran']
            inputan_harga.value = str(val.control.data['harga'])
            inputan_stok.value = str(val.control.data['stok'])
            notif_produk.value = "✏️ Mode edit aktif"
            notif_produk.color = Colors.ORANGE
            page.update()

        # 🔹 Fungsi update data
        def update_data_produk(val):
            if inputan_id_produk.value == "":
                notif_produk.value = "⚠️ Pilih data yang akan diubah!"
                notif_produk.color = Colors.RED
                page.update()
            else:
                try:
                    sql = "UPDATE produk SET kode_produk=%s, nama_produk=%s, jenis_batik=%s, ukuran=%s, harga=%s, stok=%s WHERE id_produk=%s"
                    val = (inputan_kode_produk.value, inputan_nama_produk.value, inputan_jenis_batik.value,
                           inputan_ukuran.value, inputan_harga.value, inputan_stok.value, inputan_id_produk.value)
                    perintahSQL.execute(sql, val)
                    buka_koneksi.commit()
                    notif_produk.value = "✅ Data produk berhasil diperbarui!"
                    notif_produk.color = Colors.GREEN
                    page.update()
                    tampil_data_produk()
                    bersihkan_form_produk()
                except Exception as ex:
                    notif_produk.value = f"❌ Gagal update: {ex}"
                    notif_produk.color = Colors.RED
                    page.update()
                            
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
                
        # 🔹 Reset form produk
        def bersihkan_form_produk():
            inputan_id_produk.value = ""
            inputan_kode_produk.value = ""
            inputan_nama_produk.value = ""
            inputan_jenis_batik.value = None
            inputan_ukuran.value = None
            inputan_harga.value = ""
            inputan_stok.value = ""
            page.update()
            bersihkan_notif_produk()
                
        # 🔹 Layout halaman
        tampil_data_produk()
        page.add(
            Container(
                content=Column(
                    [
                        Row([Text("📑 Form Entri Produk", size=16, weight="bold")], width=400, alignment=MainAxisAlignment.START),
                        inputan_id_produk,
                        inputan_kode_produk,
                        inputan_nama_produk,
                        inputan_jenis_batik,
                        inputan_ukuran,
                        inputan_harga,
                        inputan_stok,
                        Row(
                            [
                                ElevatedButton("💾 Simpan", on_click=simpan_data_produk, bgcolor=Colors.GREEN, color=Colors.WHITE),
                                ElevatedButton("♻️ Update", on_click=update_data_produk, bgcolor=Colors.ORANGE, color=Colors.WHITE),
                                ElevatedButton("❌ Batal", on_click=lambda e: bersihkan_form_produk(), bgcolor=Colors.GREY_500, color=Colors.WHITE),
                            ],
                            alignment=MainAxisAlignment.CENTER,
                        ),
                        notif_produk,
                        Divider(),
                        Row([Text("📋 Daftar Produk", size=16, weight="bold")], width=400, alignment=MainAxisAlignment.START),
                        Row([tabel_produk], scroll=ScrollMode.ALWAYS, width=400),
                    ],
                    scroll=ScrollMode.ALWAYS,
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                alignment=alignment.top_center,
                expand=True,
            )
        )
        page.update()

    # =========================================================
    # 👥 Halaman Kelola Pelanggan (CRUD)
    # =========================================================
    def buka_kelola_pelanggan():
        tampil_loading("Memuat kelola pelanggan 👥")
        Timer(1, halaman_kelola_pelanggan).start()

    def halaman_kelola_pelanggan():
        page.controls.clear()

        page.add(
            AppBar(
                leading=Row([
                    IconButton(icon=Icons.ARROW_BACK, tooltip="Kembali", on_click=lambda e: tampilkan_halaman(halaman_sebelumnya["index"])),
                    Text("Kembali", style=FontWeight.BOLD, size=16)
                ],
                alignment=MainAxisAlignment.START,
                spacing=0,
                ),
                bgcolor=Colors.BLUE_300,
            )
        )

        # 🔹 Kolom inputan untuk form entri pelanggan
        inputan_id_pelanggan = TextField(label="ID Pelanggan", width=300, visible=False)
        inputan_nama_pelanggan = TextField(label="Nama Pelanggan", width=300)
        inputan_jenis_kelamin = Dropdown(
            label="Jenis Kelamin",
            width=300,
            options=[
                dropdown.Option("Laki-laki"),
                dropdown.Option("Perempuan"),
            ]
        )
        inputan_no_hp = TextField(label="No HP", width=300, keyboard_type=KeyboardType.PHONE)
        inputan_email = TextField(label="Email", width=300, keyboard_type=KeyboardType.EMAIL)
        inputan_alamat = TextField(label="Alamat", width=300, multiline=True, min_lines=2, max_lines=4)
        
        notif_pelanggan = Text("")
        def atur_notif_pelanggan():
            notif_pelanggan.value = ""
            page.update()
        def bersihkan_notif_pelanggan():
            Timer(3, atur_notif_pelanggan).start()
        
        # 🔹 Tabel data pelanggan
        tabel_pelanggan = DataTable(
            columns=[
                DataColumn(Text("No.")),
                DataColumn(Text("Nama")),
                DataColumn(Text("JK")),
                DataColumn(Text("No HP")),
                DataColumn(Text("Email")),
                DataColumn(Text("Alamat")),
                DataColumn(Text("Aksi")),
            ],
            rows=[],
            width=800,
        )

        def tampil_data_pelanggan():
            perintahSQL.execute("SELECT * FROM pelanggan ORDER BY id_pelanggan DESC")
            hasil_data = perintahSQL.fetchall()
            kolom_tabel = [column[0] for column in perintahSQL.description]
            baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil_data]
                
            tabel_pelanggan.rows.clear()
            no_urut = 1
            for row in baris_tabel:
                tombol_ubah = IconButton(icon=Icons.EDIT, tooltip="Ubah", on_click=isi_form_edit_pelanggan, data=row)
                tombol_hapus = IconButton(icon=Icons.DELETE, tooltip="Hapus", icon_color=Colors.RED, on_click=hapus_data_pelanggan, data=row)

                tabel_pelanggan.rows.append(
                    DataRow(
                        cells=[
                            DataCell(Text(no_urut)),
                            DataCell(Text(row["nama_pelanggan"])),
                            DataCell(Text(row["jenis_kelamin"][:1])),
                            DataCell(Text(row["no_hp"])),
                            DataCell(Text(row["email"] or "-")),
                            DataCell(Text(row["alamat"][:20] + "..." if len(row["alamat"]) > 20 else row["alamat"])),
                            DataCell(Row([tombol_ubah, tombol_hapus])),
                        ]
                    )
                )
                no_urut += 1
            page.update()

        def simpan_data_pelanggan(val):
            if (inputan_id_pelanggan.value != ""):
                notif_pelanggan.value = "⚠️ Kamu dalam mode edit data!"
                notif_pelanggan.color = Colors.RED
                page.update()
            elif (inputan_nama_pelanggan.value == "" or inputan_jenis_kelamin.value is None or 
                  inputan_no_hp.value == "" or inputan_alamat.value == ""):
                notif_pelanggan.value = "⚠️ Kolom wajib harus diisi!"
                notif_pelanggan.color = Colors.RED
                page.update()
            else:
                try:
                    sql = "INSERT INTO pelanggan (nama_pelanggan, jenis_kelamin, no_hp, email, alamat) VALUES (%s, %s, %s, %s, %s)"
                    val = (inputan_nama_pelanggan.value, inputan_jenis_kelamin.value, inputan_no_hp.value, 
                           inputan_email.value, inputan_alamat.value)
                    perintahSQL.execute(sql, val)
                    buka_koneksi.commit()
                    notif_pelanggan.value = "✅ Data pelanggan berhasil disimpan!"
                    notif_pelanggan.color = Colors.GREEN
                    tampil_data_pelanggan()
                    page.update()
                    bersihkan_form_pelanggan()
                except Exception as ex:
                    notif_pelanggan.value = f"❌ Gagal menyimpan: {ex}"
                    notif_pelanggan.color = Colors.RED
                    page.update()
                    
        def isi_form_edit_pelanggan(val):
            inputan_id_pelanggan.value = val.control.data['id_pelanggan']
            inputan_nama_pelanggan.value = val.control.data['nama_pelanggan']
            inputan_jenis_kelamin.value = val.control.data['jenis_kelamin']
            inputan_no_hp.value = val.control.data['no_hp']
            inputan_email.value = val.control.data['email'] or ""
            inputan_alamat.value = val.control.data['alamat']
            notif_pelanggan.value = "✏️ Mode edit aktif"
            notif_pelanggan.color = Colors.ORANGE
            page.update()

        def update_data_pelanggan(val):
            if inputan_id_pelanggan.value == "":
                notif_pelanggan.value = "⚠️ Pilih data yang akan diubah!"
                notif_pelanggan.color = Colors.RED
                page.update()
            else:
                try:
                    sql = "UPDATE pelanggan SET nama_pelanggan=%s, jenis_kelamin=%s, no_hp=%s, email=%s, alamat=%s WHERE id_pelanggan=%s"
                    val = (inputan_nama_pelanggan.value, inputan_jenis_kelamin.value, inputan_no_hp.value,
                           inputan_email.value, inputan_alamat.value, inputan_id_pelanggan.value)
                    perintahSQL.execute(sql, val)
                    buka_koneksi.commit()
                    notif_pelanggan.value = "✅ Data pelanggan berhasil diperbarui!"
                    notif_pelanggan.color = Colors.GREEN
                    page.update()
                    tampil_data_pelanggan()
                    bersihkan_form_pelanggan()
                except Exception as ex:
                    notif_pelanggan.value = f"❌ Gagal update: {ex}"
                    notif_pelanggan.color = Colors.RED
                    page.update()
                            
        def hapus_data_pelanggan(val):
            try:
                perintahSQL.execute("DELETE FROM pelanggan WHERE id_pelanggan=%s", (val.control.data['id_pelanggan'],))
                buka_koneksi.commit()
                notif_pelanggan.value = f"🗑️ Data pelanggan {val.control.data['nama_pelanggan']} berhasil dihapus!"
                notif_pelanggan.color = Colors.GREEN
                page.update()
                tampil_data_pelanggan()
                bersihkan_form_pelanggan()
            except Exception as ex:
                notif_pelanggan.value = f"❌ Gagal menghapus: {ex}"
                notif_pelanggan.color = Colors.RED
                page.update()
                
        def bersihkan_form_pelanggan():
            inputan_id_pelanggan.value = ""
            inputan_nama_pelanggan.value = ""
            inputan_jenis_kelamin.value = None
            inputan_no_hp.value = ""
            inputan_email.value = ""
            inputan_alamat.value = ""
            page.update()
            bersihkan_notif_pelanggan()
                
        tampil_data_pelanggan()
        page.add(
            Container(
                content=Column(
                    [
                        Row([Text("📑 Form Entri Pelanggan", size=16, weight="bold")], width=400, alignment=MainAxisAlignment.START),
                        inputan_id_pelanggan,
                        inputan_nama_pelanggan,
                        inputan_jenis_kelamin,
                        inputan_no_hp,
                        inputan_email,
                        inputan_alamat,
                        Row(
                            [
                                ElevatedButton("💾 Simpan", on_click=simpan_data_pelanggan, bgcolor=Colors.GREEN, color=Colors.WHITE),
                                ElevatedButton("♻️ Update", on_click=update_data_pelanggan, bgcolor=Colors.ORANGE, color=Colors.WHITE),
                                ElevatedButton("❌ Batal", on_click=lambda e: bersihkan_form_pelanggan(), bgcolor=Colors.GREY_500, color=Colors.WHITE),
                            ],
                            alignment=MainAxisAlignment.CENTER,
                        ),
                        notif_pelanggan,
                        Divider(),
                        Row([Text("📋 Daftar Pelanggan", size=16, weight="bold")], width=400, alignment=MainAxisAlignment.START),
                        Row([tabel_pelanggan], scroll=ScrollMode.ALWAYS, width=400),
                    ],
                    scroll=ScrollMode.ALWAYS,
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                alignment=alignment.top_center,
                expand=True,
            )
        )
        page.update()

    # =========================================================
    # 💰 Halaman Transaksi Kasir
    # =========================================================
    def halaman_transaksi():
        page.controls.clear()

        # Judul dinamis untuk AppBar
        judul = "💰 Transaksi Kasir"
        if hak_akses == "kasir":
            judul = "💰 Kasir - Transaksi"

        appbar = AppBar(
            title=Text(f"{judul}", size=16),
            bgcolor=Colors.BLUE_300,
            center_title=True,
            actions=[
                PopupMenuButton(
                    items=[
                        PopupMenuItem(text=f"{username}"),
                        PopupMenuItem(),
                        PopupMenuItem(text="↩️ Keluar", checked=False, on_click=logout),
                    ]
                ),
            ],
        )
        page.add(appbar)

        # 🔹 Keranjang Belanja
        keranjang = []
        
        # 🔹 Inputan untuk transaksi
        inputan_dropdown_pelanggan = None
        inputan_dropdown_produk = None
        inputan_jumlah_beli = TextField(label="Jumlah Beli", width=140, keyboard_type=KeyboardType.NUMBER, value="1")
        inputan_diskon_item = TextField(label="Diskon (Rp)", width=140, keyboard_type=KeyboardType.NUMBER, value="0")
        inputan_metode_pembayaran = Dropdown(
            label="Metode Pembayaran",
            width=300,
            options=[
                dropdown.Option("Tunai"),
                dropdown.Option("Transfer Bank"),
                dropdown.Option("E-Wallet"),
                dropdown.Option("Kartu Kredit"),
                dropdown.Option("Kartu Debit"),
            ]
        )
        
        notif_transaksi = Text("")
        def atur_notif_transaksi():
            notif_transaksi.value = ""
            page.update()
        def bersihkan_notif_transaksi():
            Timer(3, atur_notif_transaksi).start()

        # 🔹 Tabel keranjang
        tabel_keranjang = DataTable(
            columns=[
                DataColumn(Text("No.")),
                DataColumn(Text("Produk")),
                DataColumn(Text("Harga")),
                DataColumn(Text("Qty")),
                DataColumn(Text("Diskon")),
                DataColumn(Text("Total")),
                DataColumn(Text("Aksi")),
            ],
            rows=[],
            width=800,
        )

        # Label total
        label_total_item = Text("Total Item: 0", size=16, weight="bold")
        label_total_bayar = Text("Total Bayar: Rp 0", size=18, weight="bold", color=Colors.GREEN)

        def update_dropdown_pelanggan():
            perintahSQL.execute("SELECT * FROM pelanggan ORDER BY nama_pelanggan ASC")
            hasil = perintahSQL.fetchall()
            kolom_tabel = [column[0] for column in perintahSQL.description]
            baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil]
            return Dropdown(
                label="Pilih Pelanggan",
                hint_text="Pilih pelanggan...",
                width=300,
                options=[
                    dropdown.Option(row["id_pelanggan"], f"{row['nama_pelanggan']} - {row['no_hp']}")
                    for row in baris_tabel
                ],
            )

        def update_dropdown_produk():
            perintahSQL.execute("SELECT * FROM produk WHERE stok > 0 ORDER BY nama_produk ASC")
            hasil = perintahSQL.fetchall()
            kolom_tabel = [column[0] for column in perintahSQL.description]
            baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil]
            return Dropdown(
                label="Pilih Produk",
                hint_text="Pilih produk...",
                width=300,
                options=[
                    dropdown.Option(
                        row["id_produk"], 
                        f"{row['nama_produk']} - Rp {row['harga']:,.0f} (Stok: {row['stok']})"
                    )
                    for row in baris_tabel
                ],
            )

        def tampil_keranjang():
            tabel_keranjang.rows.clear()
            no_urut = 1
            total_item = 0
            total_bayar = 0

            for item in keranjang:
                tombol_hapus = IconButton(
                    icon=Icons.DELETE,
                    tooltip="Hapus",
                    icon_color=Colors.RED,
                    on_click=lambda e, idx=no_urut-1: hapus_dari_keranjang(idx)
                )

                tabel_keranjang.rows.append(
                    DataRow(
                        cells=[
                            DataCell(Text(no_urut)),
                            DataCell(Text(item["nama_produk"])),
                            DataCell(Text(f"Rp {item['harga_satuan']:,.0f}")),
                            DataCell(Text(item["jumlah_beli"])),
                            DataCell(Text(f"Rp {item['diskon_item']:,.0f}")),
                            DataCell(Text(f"Rp {item['total_item']:,.0f}")),
                            DataCell(tombol_hapus),
                        ]
                    )
                )
                no_urut += 1
                total_item += item["jumlah_beli"]
                total_bayar += item["total_item"]

            label_total_item.value = f"Total Item: {total_item}"
            label_total_bayar.value = f"Total Bayar: Rp {total_bayar:,.0f}"
            page.update()

        def tambah_ke_keranjang(val):
            nonlocal inputan_dropdown_produk

            if inputan_dropdown_produk.value is None:
                notif_transaksi.value = "⚠️ Pilih produk terlebih dahulu!"
                notif_transaksi.color = Colors.RED
                page.update()
                bersihkan_notif_transaksi()
                return

            if inputan_jumlah_beli.value == "" or int(inputan_jumlah_beli.value) <= 0:
                notif_transaksi.value = "⚠️ Jumlah beli harus lebih dari 0!"
                notif_transaksi.color = Colors.RED
                page.update()
                bersihkan_notif_transaksi()
                return

            try:
                perintahSQL.execute("SELECT * FROM produk WHERE id_produk=%s", (inputan_dropdown_produk.value,))
                produk = perintahSQL.fetchone()
                kolom = [column[0] for column in perintahSQL.description]
                produk_dict = dict(zip(kolom, produk))

                jumlah_beli = int(inputan_jumlah_beli.value)
                diskon_item = float(inputan_diskon_item.value) if inputan_diskon_item.value else 0

                if jumlah_beli > produk_dict["stok"]:
                    notif_transaksi.value = f"⚠️ Stok tidak mencukupi! Stok tersedia: {produk_dict['stok']}"
                    notif_transaksi.color = Colors.RED
                    page.update()
                    bersihkan_notif_transaksi()
                    return

                subtotal = float(produk_dict["harga"]) * jumlah_beli
                total_item = subtotal - diskon_item

                item_keranjang = {
                    "id_produk": produk_dict["id_produk"],
                    "kode_produk": produk_dict["kode_produk"],
                    "nama_produk": produk_dict["nama_produk"],
                    "jumlah_beli": jumlah_beli,
                    "harga_satuan": float(produk_dict["harga"]),
                    "subtotal": subtotal,
                    "diskon_item": diskon_item,
                    "total_item": total_item,
                }

                keranjang.append(item_keranjang)
                tampil_keranjang()

                # Reset inputan
                inputan_jumlah_beli.value = "1"
                inputan_diskon_item.value = "0"
                
                # Refresh dropdown produk
                dropdown_produk_baru = update_dropdown_produk()
                form_controls = page.controls[1].content.controls
                idx = form_controls.index(inputan_dropdown_produk)
                form_controls[idx] = dropdown_produk_baru
                inputan_dropdown_produk = dropdown_produk_baru
                
                notif_transaksi.value = "✅ Produk ditambahkan ke keranjang!"
                notif_transaksi.color = Colors.GREEN
                page.update()
                bersihkan_notif_transaksi()

            except Exception as ex:
                notif_transaksi.value = f"❌ Gagal menambahkan: {ex}"
                notif_transaksi.color = Colors.RED
                page.update()
                bersihkan_notif_transaksi()

        def hapus_dari_keranjang(index):
            keranjang.pop(index)
            tampil_keranjang()
            notif_transaksi.value = "🗑️ Item dihapus dari keranjang!"
            notif_transaksi.color = Colors.ORANGE
            page.update()
            bersihkan_notif_transaksi()

        def proses_transaksi(val):
            nonlocal inputan_dropdown_pelanggan, inputan_dropdown_produk

            if inputan_dropdown_pelanggan.value is None:
                notif_transaksi.value = "⚠️ Pilih pelanggan terlebih dahulu!"
                notif_transaksi.color = Colors.RED
                page.update()
                bersihkan_notif_transaksi()
                return

            if len(keranjang) == 0:
                notif_transaksi.value = "⚠️ Keranjang masih kosong!"
                notif_transaksi.color = Colors.RED
                page.update()
                bersihkan_notif_transaksi()
                return

            if inputan_metode_pembayaran.value is None:
                notif_transaksi.value = "⚠️ Pilih metode pembayaran!"
                notif_transaksi.color = Colors.RED
                page.update()
                bersihkan_notif_transaksi()
                return

            try:
                # Generate kode transaksi
                waktu = datetime.now().strftime("%d%H%M%S")
                kode_transaksi = f"TRX{waktu}"

                # Hitung total
                total_item = sum(item["jumlah_beli"] for item in keranjang)
                total_bayar = sum(item["total_item"] for item in keranjang)

                # Insert ke tabel transaksi
                sql_transaksi = "INSERT INTO transaksi (kode_transaksi, id_pelanggan, total_item, total_bayar, metode_pembayaran) VALUES (%s, %s, %s, %s, %s)"
                val_transaksi = (kode_transaksi, inputan_dropdown_pelanggan.value, total_item, total_bayar, inputan_metode_pembayaran.value)
                perintahSQL.execute(sql_transaksi, val_transaksi)
                id_transaksi = perintahSQL.lastrowid

                # Insert detail transaksi & update stok
                for item in keranjang:
                    sql_detail = "INSERT INTO detail_transaksi (id_transaksi, id_produk, kode_produk, nama_produk, jumlah_beli, harga_satuan, subtotal, diskon_item, total_item) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    val_detail = (
                        id_transaksi,
                        item["id_produk"],
                        item["kode_produk"],
                        item["nama_produk"],
                        item["jumlah_beli"],
                        item["harga_satuan"],
                        item["subtotal"],
                        item["diskon_item"],
                        item["total_item"]
                    )
                    perintahSQL.execute(sql_detail, val_detail)

                    # Update stok produk
                    sql_update_stok = "UPDATE produk SET stok = stok - %s WHERE id_produk = %s"
                    perintahSQL.execute(sql_update_stok, (item["jumlah_beli"], item["id_produk"]))

                buka_koneksi.commit()

                # Reset form
                keranjang.clear()
                tampil_keranjang()
                
                # Refresh dropdown
                dropdown_pelanggan_baru = update_dropdown_pelanggan()
                dropdown_produk_baru = update_dropdown_produk()
                form_controls = page.controls[1].content.controls
                
                idx_pelanggan = form_controls.index(inputan_dropdown_pelanggan)
                form_controls[idx_pelanggan] = dropdown_pelanggan_baru
                inputan_dropdown_pelanggan = dropdown_pelanggan_baru
                
                idx_produk = form_controls.index(inputan_dropdown_produk)
                form_controls[idx_produk] = dropdown_produk_baru
                inputan_dropdown_produk = dropdown_produk_baru
                
                inputan_metode_pembayaran.value = None

                notif_transaksi.value = f"✅ Transaksi berhasil! Kode: {kode_transaksi}"
                notif_transaksi.color = Colors.GREEN
                page.update()
                Timer(5, atur_notif_transaksi).start()

            except Exception as ex:
                notif_transaksi.value = f"❌ Transaksi gagal: {ex}"
                notif_transaksi.color = Colors.RED
                page.update()
                bersihkan_notif_transaksi()

        # Inisialisasi dropdown
        inputan_dropdown_pelanggan = update_dropdown_pelanggan()
        inputan_dropdown_produk = update_dropdown_produk()

        page.add(
            Container(
                content=Column(
                    [
                        Row([
                            ElevatedButton("➕ Kelola Produk", on_click=lambda e: buka_kelola_produk(), bgcolor=Colors.GREEN, color=Colors.WHITE),
                            ElevatedButton("👥 Kelola Pelanggan", on_click=lambda e: buka_kelola_pelanggan(), bgcolor=Colors.BLUE, color=Colors.WHITE),
                        ], alignment=MainAxisAlignment.CENTER),
                        Divider(),
                        Row([Text("🛒 Form Transaksi", size=16, weight="bold")], width=400, alignment=MainAxisAlignment.START),
                        inputan_dropdown_pelanggan,
                        Row([Text("Pilih Produk & Tambah ke Keranjang", size=14, weight="bold")], width=400),
                        inputan_dropdown_produk,
                        Row([
                            inputan_jumlah_beli,
                            inputan_diskon_item,
                        ], alignment=MainAxisAlignment.CENTER),
                        ElevatedButton("🛒 Tambah ke Keranjang", on_click=tambah_ke_keranjang, bgcolor=Colors.BLUE, color=Colors.WHITE, width=300),
                        Divider(),
                        Row([Text("🛒 Keranjang Belanja", size=16, weight="bold")], width=400, alignment=MainAxisAlignment.START),
                        Row([tabel_keranjang], scroll=ScrollMode.ALWAYS, width=400),
                        label_total_item,
                        label_total_bayar,
                        Divider(),
                        inputan_metode_pembayaran,
                        ElevatedButton("💰 Proses Transaksi", on_click=proses_transaksi, bgcolor=Colors.GREEN, color=Colors.WHITE, width=300, height=50),
                        notif_transaksi,
                    ],
                    scroll=ScrollMode.ALWAYS,
                    alignment=MainAxisAlignment.START,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                alignment=alignment.top_center,
                expand=True,
            )
        )

        page.add(menu_bottom_bar)
        page.update()

    # =========================================================
    # 📊 Halaman Laporan Transaksi
    # =========================================================
    def halaman_laporan():
        page.controls.clear()

        appbar = AppBar(
            title=Text("📊 Laporan Transaksi", size=16),
            bgcolor=Colors.BLUE_300,
            center_title=True,
            actions=[
                PopupMenuButton(
                    items=[
                        PopupMenuItem(text=f"{username}"),
                        PopupMenuItem(),
                        PopupMenuItem(text="↩️ Keluar", checked=False, on_click=logout),
                    ]
                ),
            ],
        )
        page.add(appbar)

        # 🔍 Input Pencarian
        inputan_cari = TextField(
            label="🔍 Cari (kode/pelanggan/tanggal)",
            width=300,
            on_change=lambda e: tampil_data_transaksi(),
        )

        # 🔹 Tabel transaksi
        tabel_transaksi = DataTable(
            columns=[
                DataColumn(Text("No.")),
                DataColumn(Text("Kode")),
                DataColumn(Text("Tanggal")),
                DataColumn(Text("Pelanggan")),
                DataColumn(Text("Total")),
                DataColumn(Text("Metode")),
                DataColumn(Text("Aksi")),
            ],
            rows=[],
            width=800,
        )

        def tampil_data_transaksi():
            keyword = f"%{inputan_cari.value}%" if inputan_cari.value else "%%"

            sql = """SELECT t.*, p.nama_pelanggan 
                FROM transaksi t
                JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
                WHERE t.kode_transaksi LIKE %s
                OR p.nama_pelanggan LIKE %s
                OR t.tanggal_transaksi LIKE %s
                ORDER BY t.tanggal_transaksi DESC"""

            perintahSQL.execute(sql, (keyword, keyword, keyword))
            hasil_data = perintahSQL.fetchall()
            kolom_tabel = [column[0] for column in perintahSQL.description]
            baris_tabel = [dict(zip(kolom_tabel, row)) for row in hasil_data]

            tabel_transaksi.rows.clear()
            no_urut = 1

            for row in baris_tabel:
                tombol_detail = IconButton(
                    icon=Icons.VISIBILITY,
                    tooltip="Detail",
                    on_click=lambda e, r=row: tampil_detail_transaksi(r)
                )

                tabel_transaksi.rows.append(
                    DataRow(
                        cells=[
                            DataCell(Text(no_urut)),
                            DataCell(Text(row["kode_transaksi"])),
                            DataCell(Text(row["tanggal_transaksi"].strftime("%d-%m-%Y %H:%M"))),
                            DataCell(Text(row["nama_pelanggan"])),
                            DataCell(Text(f"Rp {row['total_bayar']:,.0f}")),
                            DataCell(Text(row["metode_pembayaran"])),
                            DataCell(tombol_detail),
                        ]
                    )
                )
                no_urut += 1

            page.update()

        def tampil_detail_transaksi(transaksi):
            def tutup_dialog(e):
                dialog.open = False
                page.update()

            # Ambil detail transaksi
            perintahSQL.execute("SELECT * FROM detail_transaksi WHERE id_transaksi=%s", (transaksi["id_transaksi"],))
            hasil_detail = perintahSQL.fetchall()
            kolom = [column[0] for column in perintahSQL.description]
            detail_list = [dict(zip(kolom, row)) for row in hasil_detail]

            # Buat list detail item
            detail_items = []
            for idx, item in enumerate(detail_list, 1):
                detail_items.append(
                    Text(f"{idx}. {item['nama_produk']} x{item['jumlah_beli']} @ Rp {item['harga_satuan']:,.0f} = Rp {item['total_item']:,.0f}")
                )

            dialog = AlertDialog(
                title=Text(f"Detail Transaksi: {transaksi['kode_transaksi']}"),
                content=Column(
                    [
                        Text(f"Tanggal: {transaksi['tanggal_transaksi'].strftime('%d-%m-%Y %H:%M')}"),
                        Text(f"Pelanggan: {transaksi['nama_pelanggan']}"),
                        Text(f"Metode: {transaksi['metode_pembayaran']}"),
                        Divider(),
                        Text("Detail Produk:", weight="bold"),
                        *detail_items,
                        Divider(),
                        Text(f"Total Item: {transaksi['total_item']}", weight="bold"),
                        Text(f"Total Bayar: Rp {transaksi['total_bayar']:,.0f}", weight="bold", color=Colors.GREEN),
                    ],
                    scroll=ScrollMode.AUTO,
                    height=400,
                ),
                actions=[
                    TextButton("Tutup", on_click=tutup_dialog),
                ],
            )

            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        tampil_data_transaksi()

        page.add(
            Container(
                content=Column(
                    [
                        Row([Text("📊 Laporan Transaksi", size=16, weight="bold")], width=400, alignment=MainAxisAlignment.START),
                        inputan_cari,
                        Divider(),
                        Row([tabel_transaksi], scroll=ScrollMode.ALWAYS, width=400),
                    ],
                    scroll=ScrollMode.ALWAYS,
                    alignment=MainAxisAlignment.START,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                alignment=alignment.top_center,
                expand=True,
            )
        )

        page.add(menu_bottom_bar)
        page.update()

    # -------------------------------------------------
    # 🧭 Fungsi Halaman
    # -------------------------------------------------
    def tampilkan_halaman(index):
        # Simpan halaman saat ini sebagai halaman sebelumnya
        halaman_sebelumnya["index"] = index
        
        if index == 0:
            page.controls.clear()
            
            appbar = AppBar(
                title=Text("🏠 Beranda", size=16),
                bgcolor=Colors.BLUE_300,
                center_title=True,
                actions=[
                    PopupMenuButton(
                        items=[
                            PopupMenuItem(text=f"{username}"),
                            PopupMenuItem(),
                            PopupMenuItem(text="↩️ Keluar", checked=False, on_click=logout),
                        ]
                    ),
                ],
            )
            page.add(appbar)

            # Statistik singkat
            perintahSQL.execute("SELECT COUNT(*) FROM produk")
            total_produk = perintahSQL.fetchone()[0]
            
            perintahSQL.execute("SELECT COUNT(*) FROM pelanggan")
            total_pelanggan = perintahSQL.fetchone()[0]
            
            perintahSQL.execute("SELECT COUNT(*) FROM transaksi")
            total_transaksi = perintahSQL.fetchone()[0]
            
            perintahSQL.execute("SELECT SUM(total_bayar) FROM transaksi")
            total_pendapatan = perintahSQL.fetchone()[0] or 0

            page.add(
                Container(
                    content=Column([
                        Text("🛍️ Sistem Informasi Kasir Batik", size=24, weight="bold"),
                        Text(f"Selamat datang, {username}!", size=16),
                        Text(f"Hak Akses: {hak_akses.upper()}", size=14, color=Colors.BLUE),
                        Divider(),
                        Text("📊 Statistik", size=18, weight="bold"),
                        # Card Pendapatan (paling atas, lebar penuh)
                        Container(
                            content=Column([
                                Icon(Icons.ATTACH_MONEY, size=50, color=Colors.PURPLE),
                                Text("Total Pendapatan", weight="bold", size=16),
                                Text(f"Rp {total_pendapatan:,.0f}", size=22, weight="bold"),
                            ], horizontal_alignment=CrossAxisAlignment.CENTER),
                            bgcolor=Colors.PURPLE_100,
                            padding=25,
                            border_radius=15,
                            width=360,
                        ),
                        Text("Klik card untuk melihat detail", size=12, color=Colors.GREY, italic=True),
                        # 3 Card yang bisa diklik
                        Row([
                            Container(
                                content=Column([
                                    Icon(Icons.INVENTORY, size=40, color=Colors.BLUE),
                                    Text("Produk", weight="bold"),
                                    Text(f"{total_produk}", size=20, weight="bold"),
                                ], horizontal_alignment=CrossAxisAlignment.CENTER),
                                bgcolor=Colors.BLUE_100,
                                padding=20,
                                border_radius=10,
                                width=110,
                                ink=True,
                                on_click=lambda e: buka_kelola_produk(),
                            ),
                            Container(
                                content=Column([
                                    Icon(Icons.PEOPLE, size=40, color=Colors.GREEN),
                                    Text("Pelanggan", weight="bold"),
                                    Text(f"{total_pelanggan}", size=20, weight="bold"),
                                ], horizontal_alignment=CrossAxisAlignment.CENTER),
                                bgcolor=Colors.GREEN_100,
                                padding=20,
                                border_radius=10,
                                width=110,
                                ink=True,
                                on_click=lambda e: buka_kelola_pelanggan(),
                            ),
                            Container(
                                content=Column([
                                    Icon(Icons.RECEIPT_LONG, size=40, color=Colors.ORANGE),
                                    Text("Transaksi", weight="bold"),
                                    Text(f"{total_transaksi}", size=20, weight="bold"),
                                ], horizontal_alignment=CrossAxisAlignment.CENTER),
                                bgcolor=Colors.ORANGE_100,
                                padding=20,
                                border_radius=10,
                                width=110,
                                ink=True,
                                on_click=lambda e: halaman_laporan(),
                            ),
                        ], alignment=MainAxisAlignment.CENTER, spacing=10),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    spacing=15,
                    ),
                    alignment=alignment.center,
                    expand=True,
                )
            )

            page.add(menu_bottom_bar)
            page.update()

        elif index == 1:
            page.controls.clear()
            
            appbar = AppBar(
                title=Text("ℹ️ Tentang", size=16),
                bgcolor=Colors.BLUE_300,
                center_title=True,
                actions=[
                    PopupMenuButton(
                        items=[
                            PopupMenuItem(text=f"{username}"),
                            PopupMenuItem(),
                            PopupMenuItem(text="↩️ Keluar", checked=False, on_click=logout),
                        ]
                    ),
                ],
            )
            page.add(appbar)

            page.add(
                Container(
                    content=Column([
                        Icon(Icons.INFO_OUTLINE, size=100, color=Colors.BLUE),
                        Text("ℹ️ Tentang Aplikasi", size=24, weight="bold"),
                        Divider(),
                        Text("Sistem Informasi Kasir Batik", size=18, weight="bold"),
                        Text("Versi 1.0.0", size=14, color=Colors.GREY),
                        Divider(),
                        Text("Aplikasi ini dibuat menggunakan:", weight="bold"),
                        Text("• Python 3.x"),
                        Text("• Flet Framework"),
                        Text("• MySQL Database"),
                        Divider(),
                        Text("Fitur Aplikasi:", weight="bold"),
                        Text("• Kelola Produk Batik"),
                        Text("• Kelola Data Pelanggan"),
                        Text("• Transaksi Kasir"),
                        Text("• Laporan Transaksi"),
                        Text("• Manajemen Stok"),
                    ],
                    spacing=10,
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                    ),
                    alignment=alignment.center,
                    expand=True,
                )
            )

            page.add(menu_bottom_bar)
            page.update()

        elif index == 2:
            halaman_laporan()

        elif index == 3:
            halaman_transaksi()

    # -------------------------------------------------
    # 🔘 Bottom Navigation Bar
    # -------------------------------------------------
    def pilih_menu(val):
        tampilkan_halaman(val.control.selected_index)

    menu_bottom_bar = NavigationBar(
        destinations=[
            NavigationBarDestination(icon=Icons.HOME, label="Beranda"),
            NavigationBarDestination(icon=Icons.INFO, label="Tentang"),
            NavigationBarDestination(icon=Icons.RECEIPT_LONG, label="Laporan"),
            NavigationBarDestination(icon=Icons.SHOPPING_CART, label="Kasir"),
        ],
        on_change=pilih_menu,
        selected_index=0,
    )

    tampilkan_halaman(0)

# =========================================================
# 🔹 Halaman Login
# =========================================================
def halaman_login(page: Page):
    page.clean()
    page.title = "🔐 Login - Kasir Batik"
    page.window.height = 700
    page.window.width = 400
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER

    def tampil_loading(text=""):
        page.clean()
        page.add(
            Column(
                [
                    ProgressRing(width=60, height=60),
                    Text(text, size=16, weight=FontWeight.BOLD)
                ],
                alignment=MainAxisAlignment.CENTER,
                horizontal_alignment=CrossAxisAlignment.CENTER,
            )
        )
        page.update()

    inputan_username = TextField(label="Username", width=250)
    inputan_password = TextField(label="Password", password=True, can_reveal_password=True, width=250)
    notif_login = Text("", color=Colors.RED)

    def proses_login(val):
        # Login sederhana tanpa tabel user, bisa dikembangkan lebih lanjut
        # Default: username = admin, password = admin untuk hak_akses = kasir
        if inputan_username.value == "admin" and inputan_password.value == "admin":
            tampil_loading("Memuat halaman utama 🛍️")
            Timer(1, lambda: halaman_utama(page, "admin", "kasir")).start()
        else:
            notif_login.value = "❌ Username atau password salah!"
            page.update()
            def bersihkan_notif():
                notif_login.value = ""
                page.update()
            Timer(2, bersihkan_notif).start()

    tombol_login = ElevatedButton(
        "🔓 Login",
        on_click=proses_login,
        width=250,
        height=50,
        bgcolor=Colors.BLUE,
        color=Colors.WHITE
    )

    page.add(
        Column(
            [
                Icon(Icons.SHOPPING_BAG, size=80, color=Colors.BLUE),
                Text("🛍️ Kasir Batik", size=28, weight="bold"),
                Text("Sistem Informasi Kasir", size=14, color=Colors.GREY),
                Divider(),
                inputan_username,
                inputan_password,
                tombol_login,
                notif_login,
                Divider(),
                Text("Default Login:", size=12, color=Colors.GREY),
                Text("Username: admin | Password: admin", size=10, color=Colors.GREY),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
    )
    page.update()

# =========================================================
# 🚀 Jalankan Aplikasi
# =========================================================
app(target=halaman_login)
