from flet import *
import pymysql
from datetime import datetime, date
from threading import Timer

# =========================================================
# 🔹 Konfigurasi Koneksi Database
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",      # Sesuaikan password database Anda
        database="db_poundfit",
        cursorclass=pymysql.cursors.DictCursor
    )

# =========================================================
# 🔹 Halaman Utama (Setelah Login)
# =========================================================
def halaman_utama(page: Page, username, hak_akses):
    # Koneksi DB
    try:
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()
    except Exception as e:
        page.add(Text(f"Gagal koneksi database: {e}", color=Colors.RED))
        return

    page.clean()
    page.title = "💪 Sistem Informasi Poundfit"
    page.window.width = 360
    page.window.height = 640
    page.padding = 20
    page.theme_mode = ThemeMode.LIGHT
    page.scroll = ScrollMode.AUTO

    # Variabel navigasi
    halaman_sebelumnya = {"index": 0}

    # 🔘 Fungsi Logout
    def logout(val):
        buka_koneksi.close()
        page.clean()
        halaman_login(page)
        page.update()
    
    # 🔘 Fungsi Loading
    def tampil_loading(text=""):
        page.controls.clear()
        page.add(
            Container(
                content=Column(
                    [
                        ProgressRing(width=50, height=50, color=Colors.PINK),
                        Text(text, size=16, weight=FontWeight.BOLD)
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                ),
                alignment=alignment.center,
                expand=True
            )
        )
        page.update()

    # =========================================================
    # 🤸 Halaman Kelola Kelas Poundfit (CRUD)
    # =========================================================
    def buka_kelola_kelas():
        tampil_loading("Memuat Data Kelas...")
        Timer(0.5, halaman_kelola_kelas).start()

    def halaman_kelola_kelas():
        page.controls.clear()

        # Input Form
        inp_id = TextField(label="ID", visible=False)
        inp_nama = TextField(label="Nama Kelas", expand=True)
        inp_hari = Dropdown(
            label="Hari", expand=True,
            options=[dropdown.Option(h) for h in ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']]
        )
        inp_jam = TextField(label="Jam (HH:MM)", expand=True, hint_text="18:00")
        inp_lokasi = TextField(label="Lokasi", expand=True)
        inp_tarif = TextField(label="Tarif (Rp)", expand=True, keyboard_type=KeyboardType.NUMBER)
        inp_kapasitas = TextField(label="Kapasitas", expand=True, keyboard_type=KeyboardType.NUMBER, value="20")
        
        notif = Text("")

        # Tabel Kelas
        tabel_kelas = DataTable(
            columns=[
                DataColumn(Text("Nama", size=10)),
                DataColumn(Text("Hari", size=10)),
                DataColumn(Text("Tarif", size=10)),
                DataColumn(Text("Aksi", size=10)),
            ],
            rows=[],
            column_spacing=5,
            heading_row_height=35
        )

        def load_data_kelas():
            perintahSQL.execute("SELECT * FROM kelas_poundfit ORDER BY hari DESC")
            data = perintahSQL.fetchall()
            tabel_kelas.rows.clear()
            
            for row in data:
                tabel_kelas.rows.append(
                    DataRow(cells=[
                        DataCell(Text(row['nama_kelas'], size=10, overflow=TextOverflow.ELLIPSIS)),
                        DataCell(Column([Text(row['hari'], weight="bold", size=9), Text(str(row['jam']), size=8)], spacing=2)),
                        DataCell(Text(f"{int(row['tarif']/1000)}k", size=10)),
                        DataCell(Row([
                            IconButton(Icons.EDIT, icon_color=Colors.BLUE, on_click=isi_form, data=row, icon_size=18),
                            IconButton(Icons.DELETE, icon_color=Colors.RED, on_click=hapus_data, data=row, icon_size=18)
                        ], spacing=0))
                    ])
                )
            page.update()

        def simpan_data(e):
            try:
                if inp_id.value: # Update
                    sql = "UPDATE kelas_poundfit SET nama_kelas=%s, hari=%s, jam=%s, lokasi_kelas=%s, tarif=%s, kapasitas=%s WHERE id_kelas=%s"
                    val = (inp_nama.value, inp_hari.value, inp_jam.value, inp_lokasi.value, inp_tarif.value, inp_kapasitas.value, inp_id.value)
                    perintahSQL.execute(sql, val)
                    msg = "Data diperbarui!"
                else: # Insert
                    sql = "INSERT INTO kelas_poundfit (nama_kelas, hari, jam, lokasi_kelas, tarif, kapasitas) VALUES (%s, %s, %s, %s, %s, %s)"
                    val = (inp_nama.value, inp_hari.value, inp_jam.value, inp_lokasi.value, inp_tarif.value, inp_kapasitas.value)
                    perintahSQL.execute(sql, val)
                    msg = "Kelas baru ditambahkan!"
                
                buka_koneksi.commit()
                notif.value = msg
                notif.color = Colors.GREEN
                bersihkan_form()
                load_data_kelas()
            except Exception as ex:
                notif.value = f"Error: {ex}"
                notif.color = Colors.RED
            page.update()

        def hapus_data(e):
            try:
                perintahSQL.execute("DELETE FROM kelas_poundfit WHERE id_kelas=%s", (e.control.data['id_kelas'],))
                buka_koneksi.commit()
                load_data_kelas()
            except Exception as ex:
                page.snack_bar = SnackBar(Text(f"Gagal hapus: {ex}"))
                page.snack_bar.open = True
                page.update()

        def isi_form(e):
            d = e.control.data
            inp_id.value = str(d['id_kelas'])
            inp_nama.value = d['nama_kelas']
            inp_hari.value = d['hari']
            inp_jam.value = str(d['jam'])
            inp_lokasi.value = d['lokasi_kelas']
            inp_tarif.value = str(int(d['tarif']))
            inp_kapasitas.value = str(d['kapasitas'])
            notif.value = "Mode Edit Aktif"
            notif.color = Colors.ORANGE
            page.update()

        def bersihkan_form():
            inp_id.value = ""
            inp_nama.value = ""
            inp_hari.value = None
            inp_jam.value = ""
            inp_lokasi.value = ""
            inp_tarif.value = ""
            inp_kapasitas.value = "20"
            page.update()

        load_data_kelas()

        page.add(
            AppBar(title=Text("Kelola Kelas Poundfit"), bgcolor=Colors.PINK_600, color=Colors.WHITE,
                   leading=IconButton(Icons.ARROW_BACK, on_click=lambda e: tampilkan_halaman(0), icon_color=Colors.WHITE)),
            Container(
                content=Column([
                    Text("Form Kelas", weight="bold", size=16),
                    inp_id, inp_nama, inp_hari, inp_jam, inp_lokasi, inp_tarif, inp_kapasitas,
                    Row([ElevatedButton("Simpan", on_click=simpan_data, bgcolor=Colors.PINK), 
                         OutlinedButton("Batal", on_click=lambda e: bersihkan_form())]),
                    notif,
                    Divider(),
                    Text("Daftar Kelas", weight="bold", size=16),
                    Row([tabel_kelas], scroll=ScrollMode.ALWAYS)
                ], scroll=ScrollMode.ALWAYS),
                padding=20, expand=True
            )
        )
        page.update()

    # =========================================================
    # 👥 Halaman Kelola Peserta (CRUD)
    # =========================================================
    def buka_kelola_peserta():
        tampil_loading("Memuat Data Peserta...")
        Timer(0.5, halaman_kelola_peserta).start()

    def halaman_kelola_peserta():
        page.controls.clear()
        
        inp_id = TextField(visible=False)
        inp_nama = TextField(label="Nama Lengkap", expand=True)
        inp_jk = Dropdown(label="Jenis Kelamin", expand=True, options=[dropdown.Option("Laki-laki"), dropdown.Option("Perempuan")])
        inp_hp = TextField(label="No HP", expand=True, keyboard_type=KeyboardType.PHONE)
        inp_alamat = TextField(label="Alamat", expand=True, multiline=True, max_lines=2)
        inp_pekerjaan = TextField(label="Pekerjaan", expand=True)
        inp_status = Dropdown(label="Status", expand=True, options=[dropdown.Option("Aktif"), dropdown.Option("Nonaktif"), dropdown.Option("Trial")], value="Trial")
        
        notif = Text("")
        
        tabel_peserta = DataTable(
            columns=[DataColumn(Text("Nama", size=10)), DataColumn(Text("JK", size=10)), DataColumn(Text("Status", size=10)), DataColumn(Text("Aksi", size=10))],
            rows=[],
            column_spacing=5,
            heading_row_height=35
        )

        def load_data():
            perintahSQL.execute("SELECT * FROM peserta ORDER BY id_peserta DESC")
            data = perintahSQL.fetchall()
            tabel_peserta.rows.clear()
            for row in data:
                tabel_peserta.rows.append(DataRow(cells=[
                    DataCell(Text(row['nama_lengkap'], size=10, overflow=TextOverflow.ELLIPSIS)),
                    DataCell(Text("L" if row['jenis_kelamin'] == "Laki-laki" else "P", size=10)),
                    DataCell(Text(row['status_keanggotaan'], size=9)),
                    DataCell(Row([IconButton(Icons.EDIT, icon_color=Colors.BLUE, on_click=isi_form, data=row, icon_size=18),
                                  IconButton(Icons.DELETE, icon_color=Colors.RED, on_click=hapus_data, data=row, icon_size=18)], spacing=0))
                ]))
            page.update()

        def simpan_data(e):
            try:
                if inp_id.value:
                    sql = "UPDATE peserta SET nama_lengkap=%s, jenis_kelamin=%s, no_hp=%s, alamat=%s, pekerjaan=%s, status_keanggotaan=%s WHERE id_peserta=%s"
                    val = (inp_nama.value, inp_jk.value, inp_hp.value, inp_alamat.value, inp_pekerjaan.value, inp_status.value, inp_id.value)
                else:
                    sql = "INSERT INTO peserta (nama_lengkap, jenis_kelamin, no_hp, alamat, pekerjaan, status_keanggotaan) VALUES (%s, %s, %s, %s, %s, %s)"
                    val = (inp_nama.value, inp_jk.value, inp_hp.value, inp_alamat.value, inp_pekerjaan.value, inp_status.value)
                
                perintahSQL.execute(sql, val)
                buka_koneksi.commit()
                notif.value = "Data berhasil disimpan!"
                notif.color = Colors.GREEN
                bersihkan()
                load_data()
            except Exception as ex:
                notif.value = str(ex)
                notif.color = Colors.RED
            page.update()

        def hapus_data(e):
            try:
                perintahSQL.execute("DELETE FROM peserta WHERE id_peserta=%s", (e.control.data['id_peserta'],))
                buka_koneksi.commit()
                load_data()
            except: pass

        def isi_form(e):
            d = e.control.data
            inp_id.value = str(d['id_peserta'])
            inp_nama.value = d['nama_lengkap']
            inp_jk.value = d['jenis_kelamin']
            inp_hp.value = d['no_hp']
            inp_alamat.value = d['alamat']
            inp_pekerjaan.value = d['pekerjaan']
            inp_status.value = d['status_keanggotaan']
            page.update()

        def bersihkan():
            inp_id.value = ""
            inp_nama.value = ""
            inp_hp.value = ""
            inp_alamat.value = ""
            inp_pekerjaan.value = ""
            page.update()

        load_data()

        page.add(
            AppBar(title=Text("Kelola Peserta"), bgcolor=Colors.PINK_600, color=Colors.WHITE,
                   leading=IconButton(Icons.ARROW_BACK, on_click=lambda e: tampilkan_halaman(0), icon_color=Colors.WHITE)),
            Container(
                content=Column([
                    inp_id, inp_nama, inp_jk, inp_hp, inp_alamat, inp_pekerjaan, inp_status,
                    Row([ElevatedButton("Simpan", on_click=simpan_data, bgcolor=Colors.PINK), OutlinedButton("Reset", on_click=lambda e: bersihkan())]),
                    notif, Divider(), Row([tabel_peserta], scroll=ScrollMode.ALWAYS)
                ], scroll=ScrollMode.ALWAYS),
                padding=20, expand=True
            )
        )
        page.update()

    # =========================================================
    # 📝 Halaman Pendaftaran Kelas (Transaksi)
    # =========================================================
    def halaman_pendaftaran():
        page.controls.clear()
        
        # Dropdowns Data
        dd_peserta = Dropdown(label="Pilih Peserta", expand=True)
        dd_kelas = Dropdown(label="Pilih Kelas", expand=True)
        dd_pembayaran = Dropdown(label="Metode Pembayaran", expand=True, options=[dropdown.Option("Tunai"), dropdown.Option("Transfer"), dropdown.Option("E-Wallet")])
        
        txt_harga = Text("Harga: Rp 0", size=16, weight="bold")
        notif = Text("")

        def load_dropdowns():
            # Load Peserta
            perintahSQL.execute("SELECT id_peserta, nama_lengkap FROM peserta ORDER BY nama_lengkap ASC")
            res_peserta = perintahSQL.fetchall()
            dd_peserta.options = [dropdown.Option(p['id_peserta'], p['nama_lengkap']) for p in res_peserta]
            
            # Load Kelas (Hanya yg belum penuh)
            perintahSQL.execute("SELECT id_kelas, nama_kelas, hari, jam, tarif, kapasitas, jumlah_peserta FROM kelas_poundfit WHERE jumlah_peserta < kapasitas")
            res_kelas = perintahSQL.fetchall()
            dd_kelas.options = [
                dropdown.Option(
                    k['id_kelas'], 
                    f"{k['nama_kelas']} ({k['hari']} {k['jam']}) - Rp {k['tarif']:,.0f} [Sisa: {k['kapasitas']-k['jumlah_peserta']}]"
                ) for k in res_kelas
            ]
            dd_kelas.data = {str(k['id_kelas']): k['tarif'] for k in res_kelas}

        def cek_harga(e):
            if dd_kelas.value:
                harga = dd_kelas.data.get(dd_kelas.value, 0)
                txt_harga.value = f"Total Tagihan: Rp {harga:,.0f}"
                page.update()

        dd_kelas.on_change = cek_harga

        def proses_daftar(e):
            if not dd_peserta.value or not dd_kelas.value or not dd_pembayaran.value:
                notif.value = "Mohon lengkapi semua data!"
                notif.color = Colors.RED
                page.update()
                return

            try:
                # Generate Kode
                kode = f"REG{datetime.now().strftime('%d%H%M%S')}"
                id_p = int(dd_peserta.value)
                id_k = int(dd_kelas.value)
                
                # Ambil nama peserta dari database
                perintahSQL.execute("SELECT nama_lengkap FROM peserta WHERE id_peserta=%s", (id_p,))
                result = perintahSQL.fetchone()
                nama_p = result['nama_lengkap'] if result else ""
                
                # Tanggal
                tgl_mulai = date.today()
                tgl_akhir = date.today() # Bisa disesuaikan logicnya jika sistem paket

                # Insert Pendaftaran
                sql = """INSERT INTO pendaftaran 
                         (id_peserta, id_kelas, nama_peserta, metode_pembayaran, status_pembayaran, 
                          tanggal_mulai, tanggal_berakhir, kode_pendaftaran, status_kehadiran)
                         VALUES (%s, %s, %s, %s, 'Lunas', %s, %s, %s, 'Belum Dimulai')"""
                val = (id_p, id_k, nama_p, dd_pembayaran.value, tgl_mulai, tgl_akhir, kode)
                perintahSQL.execute(sql, val)

                # Update Jumlah Peserta di Kelas
                perintahSQL.execute("UPDATE kelas_poundfit SET jumlah_peserta = jumlah_peserta + 1 WHERE id_kelas=%s", (id_k,))
                
                buka_koneksi.commit()
                
                notif.value = f"✅ Pendaftaran Berhasil! Kode: {kode}"
                notif.color = Colors.GREEN
                
                # Reset
                dd_peserta.value = None
                dd_kelas.value = None
                dd_pembayaran.value = None
                txt_harga.value = "Total Tagihan: Rp 0"
                load_dropdowns()
                
            except Exception as ex:
                notif.value = f"Gagal: {ex}"
                notif.color = Colors.RED
            page.update()

        load_dropdowns()

        page.add(
            AppBar(
                title=Text("📝 Pendaftaran Baru"), 
                bgcolor=Colors.PINK_600, 
                color=Colors.WHITE,
                leading=Container() # Hide back button on main tabs
            ),
            Container(
                content=Column([
                    Icon(Icons.FITNESS_CENTER, size=50, color=Colors.PINK),
                    Text("Form Pendaftaran", size=18, weight="bold"),
                    Divider(),
                    Row([
                        ElevatedButton("👥 Kelola Peserta", on_click=lambda e: buka_kelola_peserta(), bgcolor=Colors.BLUE, color=Colors.WHITE, expand=True),
                        ElevatedButton("🤸 Kelola Kelas", on_click=lambda e: buka_kelola_kelas(), bgcolor=Colors.GREEN, color=Colors.WHITE, expand=True),
                    ], spacing=10),
                    Divider(),
                    dd_peserta,
                    dd_kelas,
                    txt_harga,
                    dd_pembayaran,
                    Divider(),
                    ElevatedButton("Proses Pendaftaran", on_click=proses_daftar, bgcolor=Colors.PINK, color=Colors.WHITE, height=45, expand=True),
                    notif
                ], horizontal_alignment=CrossAxisAlignment.CENTER, scroll=ScrollMode.AUTO),
                padding=20, expand=True
            ),
            menu_bottom_bar
        )
        page.update()

    # =========================================================
    # 📊 Halaman Laporan
    # =========================================================
    def halaman_laporan():
        page.controls.clear()
        
        tabel_laporan = DataTable(
            columns=[
                DataColumn(Text("Kode", size=10)),
                DataColumn(Text("Nama", size=10)),
                DataColumn(Text("Kelas", size=10)),
                DataColumn(Text("Status", size=10)),
            ],
            rows=[],
            column_spacing=5,
            heading_row_height=35
        )

        def load_laporan():
            sql = """SELECT p.kode_pendaftaran, p.nama_peserta, k.nama_kelas, p.status_pembayaran
                     FROM pendaftaran p
                     JOIN kelas_poundfit k ON p.id_kelas = k.id_kelas
                     ORDER BY p.tanggal_daftar DESC"""
            perintahSQL.execute(sql)
            data = perintahSQL.fetchall()
            
            tabel_laporan.rows.clear()
            for row in data:
                tabel_laporan.rows.append(DataRow(cells=[
                    DataCell(Text(row['kode_pendaftaran'], size=9, overflow=TextOverflow.ELLIPSIS)),
                    DataCell(Text(row['nama_peserta'], size=9, overflow=TextOverflow.ELLIPSIS)),
                    DataCell(Text(row['nama_kelas'], size=9, overflow=TextOverflow.ELLIPSIS)),
                    DataCell(Container(content=Text(row['status_pembayaran'], size=8, color=Colors.WHITE), 
                                       bgcolor=Colors.GREEN if row['status_pembayaran']=='Lunas' else Colors.ORANGE,
                                       padding=3, border_radius=3))
                ]))
            page.update()

        load_laporan()

        page.add(
            AppBar(title=Text("📊 Laporan Pendaftaran"), bgcolor=Colors.PINK_600, color=Colors.WHITE, leading=Container()),
            Container(
                content=Column([
                    Row([tabel_laporan], scroll=ScrollMode.ALWAYS)
                ], scroll=ScrollMode.ALWAYS),
                padding=10, expand=True
            ),
            menu_bottom_bar
        )
        page.update()

    # =========================================================
    # 🧭 Logika Navigasi Utama
    # =========================================================
    def tampilkan_halaman(index):
        if index == 0: # Beranda
            page.controls.clear()
            
            # Statistik
            perintahSQL.execute("SELECT COUNT(*) as tot FROM kelas_poundfit")
            tot_kelas = perintahSQL.fetchone()['tot']
            perintahSQL.execute("SELECT COUNT(*) as tot FROM peserta")
            tot_peserta = perintahSQL.fetchone()['tot']
            perintahSQL.execute("SELECT COUNT(*) as tot FROM pendaftaran")
            tot_daftar = perintahSQL.fetchone()['tot']

            # Komponen Card
            def card_menu(icon, title, count, func):
                return Container(
                    content=Column([
                        Icon(icon, size=35, color=Colors.WHITE),
                        Text(title, color=Colors.WHITE, weight="bold", size=12),
                        Text(str(count), color=Colors.WHITE, size=18, weight="bold")
                    ], horizontal_alignment=CrossAxisAlignment.CENTER, alignment=MainAxisAlignment.CENTER),
                    width=105, height=105, bgcolor=Colors.PINK_400, border_radius=12,
                    on_click=lambda e: func(), ink=True, padding=8
                )

            page.add(
                AppBar(
                    title=Text("Beranda Poundfit"), 
                    bgcolor=Colors.PINK_600, 
                    color=Colors.WHITE,
                    actions=[IconButton(Icons.LOGOUT, icon_color=Colors.WHITE, on_click=logout)]
                ),
                Container(
                    content=Column([
                        Text(f"Hai, {username}!", size=18, weight="bold"),
                        Text("Dashboard Instruktur", color=Colors.GREY, size=12),
                        Divider(),
                        Row([
                            card_menu(Icons.CLASS_, "Kelas", tot_kelas, buka_kelola_kelas),
                            card_menu(Icons.PEOPLE, "Peserta", tot_peserta, buka_kelola_peserta),
                        ], alignment=MainAxisAlignment.CENTER),
                        Row([
                            card_menu(Icons.RECEIPT_LONG, "Transaksi", tot_daftar, lambda: tampilkan_halaman(2)),
                        ], alignment=MainAxisAlignment.CENTER),
                    ], spacing=20, horizontal_alignment=CrossAxisAlignment.CENTER),
                    padding=20, expand=True, alignment=alignment.center
                ),
                menu_bottom_bar
            )
            page.update()
        
        elif index == 1: # Pendaftaran (Transaksi)
            halaman_pendaftaran()
        elif index == 2: # Laporan
            halaman_laporan()

    def navigasi_bar(e):
        tampilkan_halaman(e.control.selected_index)

    menu_bottom_bar = NavigationBar(
        destinations=[
            NavigationBarDestination(icon=Icons.HOME, label="Beranda"),
            NavigationBarDestination(icon=Icons.ADD_CIRCLE_OUTLINE, label="Daftar Baru"),
            NavigationBarDestination(icon=Icons.ANALYTICS, label="Laporan"),
        ],
        on_change=navigasi_bar,
        selected_index=0,
        bgcolor=Colors.PINK_50
    )

    tampilkan_halaman(0)

# =========================================================
# 🔐 Halaman Login
# =========================================================
def halaman_login(page: Page):
    page.title = "Login Poundfit System"
    page.window.width = 360
    page.window.height = 640
    page.clean()
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER

    user_val = TextField(label="Username", prefix_icon=Icons.PERSON, width=300)
    pass_val = TextField(label="Password", prefix_icon=Icons.LOCK, password=True, can_reveal_password=True, width=300)
    msg = Text("", color=Colors.RED)

    def login_klik(e):
        try:
            conn = koneksi_database()
            cur = conn.cursor()
            # Cek User (jika tabel kosong, buat user admin default)
            cur.execute("SELECT count(*) as tot FROM user")
            if cur.fetchone()['tot'] == 0:
                cur.execute("INSERT INTO user (username, password, hak_akses) VALUES ('admin', 'admin', 'admin')")
                conn.commit()

            cur.execute("SELECT * FROM user WHERE username=%s AND password=%s", (user_val.value, pass_val.value))
            akun = cur.fetchone()
            conn.close()

            if akun:
                halaman_utama(page, akun['username'], akun['hak_akses'])
            else:
                msg.value = "Username / Password Salah!"
                page.update()
        except Exception as ex:
            msg.value = f"Database Error: {ex}"
            page.update()

    page.add(
        Column([
            Icon(Icons.FITNESS_CENTER, size=60, color=Colors.PINK),
            Text("POUNDFIT SYSTEM", size=20, weight="bold", color=Colors.PINK_800),
            Divider(height=15, color="transparent"),
            user_val,
            pass_val,
            ElevatedButton("LOGIN", on_click=login_klik, width=300, bgcolor=Colors.PINK, color=Colors.WHITE, height=45),
            msg
            # Text("Default: admin / admin", size=11, color=Colors.GREY)
        ], alignment=MainAxisAlignment.CENTER, horizontal_alignment=CrossAxisAlignment.CENTER)
    )

app(target=halaman_login)