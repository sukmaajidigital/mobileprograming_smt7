import pymysql
from flet import *
from datetime import date


# =========================================================
# 🔹 Koneksi Database
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="2025_db_mad_proyek_uas"
    )


# =========================================================
# 🔹 HALAMAN KELOLA PASIEN
# =========================================================
def kelola_pasien_view(page: Page):

    selected_id = {"id": None}  # untuk edit

    # ================= PAGINATION & SEARCH STATE =================
    current_page = {"value": 1}
    limit_per_page = 10
    total_data = {"value": 0}
    keyword_cari = {"value": ""}

    # ================= FORM INPUT =================
    def buat_dropdown_jk():
        return Dropdown(
            label="Jenis Kelamin",
            options=[
                dropdown.Option("Pria"),
                dropdown.Option("Wanita"),
            ],
            prefix_icon=Icons.PEOPLE,
            width=360
        )

    inputan_nik_pasien = TextField(label="NIK Pasien", prefix_icon=Icons.BADGE, width=360)
    inputan_nama_pasien = TextField(label="Nama Pasien", prefix_icon=Icons.PERSON, width=360)
    inputan_jk_pasien = buat_dropdown_jk()
    inputan_tgl_lahir_pasien = TextField(label="Tgl. Lahir Pasien", prefix_icon=Icons.DATE_RANGE, read_only=True, width=250)
    def pilih_tanggal(e):
        if e.control.value:
            inputan_tgl_lahir_pasien.value = e.control.value.strftime("%Y-%m-%d")
            inputan_tgl_lahir_pasien.update()

    date_picker = DatePicker(
        first_date=date(1950, 1, 1),
        last_date=date.today(),
        on_change=pilih_tanggal
    )

    page.overlay.append(date_picker)

    opsi_tgl_lahir = ElevatedButton(
        "Pilih",
        icon=Icons.CALENDAR_MONTH,
        width=80,
        on_click=lambda e: page.open(date_picker)
    )

    inputan_alamat_pasien = TextField(
        label="Alamat Pasien",
        multiline=True,
        min_lines=3,
        prefix_icon=Icons.HOME,
        width=360
    )

    notif_kelola_pasien = Text("")

    # ================= INPUT SEARCH =================
    input_cari = TextField(
        hint_text="Cari NIK atau Nama Pasien...",
        prefix_icon=Icons.SEARCH,
        on_change=lambda e: proses_cari(e),
        width=350
    )

    # ================= RESET FORM =================
    def bersihkan_form():
        nonlocal inputan_jk_pasien

        inputan_nik_pasien.value = ""
        inputan_nama_pasien.value = ""
        inputan_tgl_lahir_pasien.value = None
        inputan_alamat_pasien.value = ""
        selected_id["id"] = None

        # 🔥 RESET DROPDOWN JK (REBUILD)
        dropdown_jk_baru = buat_dropdown_jk()
        idx_jk = form_column.controls.index(inputan_jk_pasien)
        form_column.controls[idx_jk] = dropdown_jk_baru
        inputan_jk_pasien = dropdown_jk_baru

        page.update()

    # ================= PROSES SEARCH =================
    def proses_cari(e):
        keyword_cari["value"] = e.control.value
        current_page["value"] = 1
        muat_data_pasien()
        page.update()

    # ================= SIMPAN / UPDATE =================
    def simpan_pasien(e):
        if not inputan_nik_pasien.value or not inputan_nama_pasien.value or not inputan_jk_pasien.value:
            notif_kelola_pasien.value = "❌ Data wajib diisi"
            notif_kelola_pasien.color = Colors.RED
            page.update()
            return
        
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()

        if selected_id["id"]:  # UPDATE
            perintahSQL.execute(
                """ UPDATE pasien SET nik_pasien=%s, nama_pasien=%s, jk_pasien=%s, 
                    tgl_lahir_pasien=%s, alamat_pasien=%s WHERE id_pasien=%s """,
                (
                    inputan_nik_pasien.value,
                    inputan_nama_pasien.value,
                    inputan_jk_pasien.value,
                    inputan_tgl_lahir_pasien.value,
                    inputan_alamat_pasien.value,
                    selected_id["id"],
                ),
            )
            notif_kelola_pasien.value = "✅ Data pasien diperbarui"
        else:  # INSERT
            perintahSQL.execute(
                """ INSERT INTO pasien (nik_pasien, nama_pasien, jk_pasien, 
                    tgl_lahir_pasien, alamat_pasien) 
                    VALUES (%s, %s, %s, %s, %s) """,
                (
                    inputan_nik_pasien.value,
                    inputan_nama_pasien.value,
                    inputan_jk_pasien.value,
                    inputan_tgl_lahir_pasien.value,
                    inputan_alamat_pasien.value,
                ),
            )
            notif_kelola_pasien.value = "✅ Data pasien ditambahkan"

        buka_koneksi.commit()
        perintahSQL.close()
        buka_koneksi.close()

        notif_kelola_pasien.color = Colors.GREEN
        bersihkan_form()
        muat_data_pasien()
        page.update()

    # ================= KONFIRMASI HAPUS =================
    def konfirmasi_hapus(id_pasien):
        dialog = AlertDialog(
            modal=True,
            title=Text("Konfirmasi"),
            content=Text("Yakin ingin menghapus data pasien ini?"),
            actions=[
                TextButton("Batal", on_click=lambda e: page.close(dialog)),
                ElevatedButton(
                    "Hapus",
                    bgcolor=Colors.RED,
                    color=Colors.WHITE,
                    on_click=lambda e: hapus_pasien(dialog, id_pasien),
                ),
            ],
        )
        page.open(dialog)

    def hapus_pasien(dialog, id_pasien):
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()
        perintahSQL.execute("DELETE FROM pasien WHERE id_pasien=%s", (id_pasien,))
        buka_koneksi.commit()
        perintahSQL.close()
        buka_koneksi.close()

        page.close(dialog)
        bersihkan_form()
        muat_data_pasien()
        page.update()

    # ================= EDIT PASIEN =================
    def edit_pasien(row):
        selected_id["id"] = row[0]
        inputan_nik_pasien.value = row[1]
        inputan_nama_pasien.value = row[2]
        inputan_jk_pasien.value = row[3]
        inputan_tgl_lahir_pasien.value = row[4]
        inputan_alamat_pasien.value = row[5]
        page.update()

    # ================= TABEL =================
    tabel_data_pasien = DataTable(
        columns=[
            DataColumn(Text("No.")),
            DataColumn(Text("NIK")),
            DataColumn(Text("Nama")),
            DataColumn(Text("JK")),
            DataColumn(Text("Tgl Lahir")),
            DataColumn(Text("Alamat")),
            DataColumn(Text("Aksi")),
        ],
        rows=[],
    )

    info_halaman = Text()

    def muat_data_pasien():
        tabel_data_pasien.rows.clear()
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()

        keyword = f"%{keyword_cari['value']}%"

        # Hitung total data (SEARCH AWARE)
        perintahSQL.execute(
            """ SELECT COUNT(*) FROM pasien 
                WHERE nik_pasien LIKE %s OR nama_pasien LIKE %s """,
            (keyword, keyword)
        )
        total_data["value"] = perintahSQL.fetchone()[0]

        offset = (current_page["value"] - 1) * limit_per_page

        perintahSQL.execute(
            """ SELECT 
                    id_pasien, nik_pasien, nama_pasien, jk_pasien, tgl_lahir_pasien, alamat_pasien 
                FROM pasien
                WHERE nik_pasien LIKE %s OR nama_pasien LIKE %s
                ORDER BY id_pasien DESC
                LIMIT %s OFFSET %s """,
            (keyword, keyword, limit_per_page, offset)
        )

        for index, row in enumerate(perintahSQL.fetchall()):
            no_urut = offset + index + 1
            tabel_data_pasien.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(no_urut)),
                        DataCell(Text(row[1])),
                        DataCell(Text(row[2])),
                        DataCell(Text(row[3])),
                        DataCell(Text(str(row[4]) if row[4] else "-")),
                        DataCell(Text(row[5])),
                        DataCell(
                            Row(
                                spacing=5,
                                controls=[
                                    IconButton(
                                        icon=Icons.EDIT,
                                        on_click=lambda e, data=row: edit_pasien(data),
                                    ),
                                    IconButton(
                                        icon=Icons.DELETE,
                                        icon_color=Colors.RED,
                                        on_click=lambda e, id=row[0]: konfirmasi_hapus(id),
                                    ),
                                ],
                            )
                        ),
                    ]
                )
            )
            
        total_halaman = max(1, (total_data["value"] + limit_per_page - 1) // limit_per_page)
        info_halaman.value = f"Halaman {current_page['value']} dari {total_halaman}"

        perintahSQL.close()
        buka_koneksi.close()

    # ================= PAGING BUTTON =================
    def prev_page(e):
        if current_page["value"] > 1:
            current_page["value"] -= 1
            muat_data_pasien()
            page.update()

    def next_page(e):
        total_halaman = max(1, (total_data["value"] + limit_per_page - 1) // limit_per_page)
        if current_page["value"] < total_halaman:
            current_page["value"] += 1
            muat_data_pasien()
            page.update()

    muat_data_pasien()

    # ================= LAYOUT =================
    form_column = Column(
        spacing=15,
        controls=[
            Text("Form Entri", size=18, weight="bold"),
            inputan_nik_pasien,
            inputan_nama_pasien,
            inputan_jk_pasien,
            Row([inputan_tgl_lahir_pasien, opsi_tgl_lahir]),
            inputan_alamat_pasien,
            Row([
                ElevatedButton("Simpan Data", icon=Icons.SAVE, on_click=simpan_pasien, color=Colors.WHITE, bgcolor=Colors.TEAL),
                ElevatedButton("Batal", icon=Icons.CLEAR, on_click=lambda e: bersihkan_form(), color=Colors.WHITE, bgcolor=Colors.BLACK),
            ]),
            notif_kelola_pasien,
        ],
    )

    return Container(
        expand=True,
        padding=20,
        content=Row(
            spacing=20,
            controls=[
                # FORM
                Container(
                    width=380,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    shadow=BoxShadow(blur_radius=20, color="black12"),
                    content=form_column
                ),

                # TABEL + SEARCH + PAGING
                Container(
                    expand=True,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    shadow=BoxShadow(blur_radius=20, color="black12"),
                    content=Column(
                        expand=True,
                        controls=[
                            Text("Data Pasien", size=18, weight="bold"),
                            input_cari,
                            Divider(),
                            Container(
                                expand=True,
                                alignment=alignment.top_left,
                                content=Row(
                                    expand=True,
                                    scroll=ScrollMode.AUTO,
                                    controls=[
                                        Column(scroll=ScrollMode.AUTO, controls=[tabel_data_pasien]),
                                    ],
                                ),
                            ),
                            
                            Divider(),
                            Row(
                                alignment="spaceBetween",
                                controls=[
                                    ElevatedButton("◀ Sebelumnya", on_click=prev_page),
                                    info_halaman,
                                    ElevatedButton("Berikutnya ▶", on_click=next_page),
                                ],
                            ),
                        ]
                    ),
                ),
            ],
        ),
    )
