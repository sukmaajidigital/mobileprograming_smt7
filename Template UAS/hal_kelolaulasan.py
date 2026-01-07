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
# 🔹 HALAMAN KELOLA RIWAYAT ULASAN PASIEN
# =========================================================
def kelola_riwayat_ulasan_view(page: Page):

    selected_id = {"id": None}

    # ================= PAGINATION & SEARCH STATE =================
    current_page = {"value": 1}
    limit_per_page = 10
    total_data = {"value": 0}
    keyword_cari = {"value": ""}

    # ================= FORM INPUT =================
    def buat_dropdown_sentimen():
        return Dropdown(
            label="Sentimen",
            options=[
                dropdown.Option("Positif"),
                dropdown.Option("Netral"),
                dropdown.Option("Negatif"),
            ],
            prefix_icon=Icons.MOOD,
            width=360
        )

    def buat_dropdown_pasien():
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()

        perintahSQL.execute("""
            SELECT id_pasien, nik_pasien, nama_pasien, jk_pasien
            FROM pasien
            ORDER BY nama_pasien ASC
        """)

        hasil = perintahSQL.fetchall()

        perintahSQL.close()
        buka_koneksi.close()

        return Dropdown(
            label="Pasien",
            hint_text="Cari pasien (NIK / Nama / JK)",
            prefix_icon=Icons.PERSON_SEARCH,
            width=360,
            enable_filter=True,
            enable_search=True,
            editable=True,
            options=[
                dropdown.Option(
                    key=str(row[0]),
                    text=f"{row[1]} - {row[2]} ({row[3]})"
                )
                for row in hasil
            ],
        )

    input_ulasan = TextField(label="Isi Ulasan", multiline=True, min_lines=4, prefix_icon=Icons.COMMENT, width=360)
    input_sentimen = buat_dropdown_sentimen()
    input_id_pasien = buat_dropdown_pasien()
    notif_ulasan = Text("")

    # ================= INPUT SEARCH =================
    input_cari = TextField(
        hint_text="Cari ulasan atau sentimen...",
        prefix_icon=Icons.SEARCH,
        width=350,
        on_change=lambda e: proses_cari(e)
    )

    # ================= RESET FORM =================
    def bersihkan_form():
        nonlocal input_sentimen, input_id_pasien
        input_ulasan.value = ""
        selected_id["id"] = None
        # 🔥 rebuild dropdown sentimen
        dropdown_sentimen_baru = buat_dropdown_sentimen()
        idx_sentimen = form_column.controls.index(input_sentimen)
        form_column.controls[idx_sentimen] = dropdown_sentimen_baru
        input_sentimen = dropdown_sentimen_baru
        # 🔥 rebuild dropdown pasien
        dropdown_pasien_baru = buat_dropdown_pasien()
        idx_pasien = form_column.controls.index(input_id_pasien)
        form_column.controls[idx_pasien] = dropdown_pasien_baru
        input_id_pasien = dropdown_pasien_baru
        page.update()

    # ================= PROSES SEARCH =================
    def proses_cari(e):
        keyword_cari["value"] = e.control.value
        current_page["value"] = 1
        muat_data_ulasan()
        page.update()

    # ================= SIMPAN / UPDATE =================
    def simpan_ulasan(e):
        if not input_ulasan.value or not input_sentimen.value or not input_id_pasien.value:
            notif_ulasan.value = "❌ Semua data wajib diisi"
            notif_ulasan.color = Colors.RED
            page.update()
            return

        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()

        if selected_id["id"]:
            perintahSQL.execute(
                """ UPDATE riwayat_ulasan 
                    SET ulasan=%s, sentimen=%s, id_pasien=%s 
                    WHERE id_riwayatulasan=%s """,
                (
                    input_ulasan.value,
                    input_sentimen.value,
                    input_id_pasien.value,
                    selected_id["id"]
                )
            )
            notif_ulasan.value = "✅ Data ulasan diperbarui"
        else:
            perintahSQL.execute(
                """ INSERT INTO riwayat_ulasan 
                    (ulasan, sentimen, tanggal_entri, id_pasien) 
                    VALUES (%s, %s, %s, %s) """,
                (
                    input_ulasan.value,
                    input_sentimen.value,
                    date.today(),
                    input_id_pasien.value
                )
            )
            notif_ulasan.value = "✅ Data ulasan ditambahkan"

        buka_koneksi.commit()
        perintahSQL.close()
        buka_koneksi.close()

        notif_ulasan.color = Colors.GREEN
        bersihkan_form()
        muat_data_ulasan()
        page.update()

    # ================= KONFIRMASI HAPUS =================
    def konfirmasi_hapus(id_ulasan):
        dialog = AlertDialog(
            modal=True,
            title=Text("Konfirmasi"),
            content=Text("Yakin ingin menghapus ulasan ini?"),
            actions=[
                TextButton("Batal", on_click=lambda e: page.close(dialog)),
                ElevatedButton(
                    "Hapus",
                    bgcolor=Colors.RED,
                    color=Colors.WHITE,
                    on_click=lambda e: hapus_ulasan(dialog, id_ulasan),
                ),
            ],
        )
        page.open(dialog)

    def hapus_ulasan(dialog, id_ulasan):
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()
        perintahSQL.execute(
            "DELETE FROM riwayat_ulasan WHERE id_riwayatulasan=%s",
            (id_ulasan,)
        )
        buka_koneksi.commit()
        perintahSQL.close()
        buka_koneksi.close()

        page.close(dialog)
        muat_data_ulasan()
        page.update()

    # ================= EDIT DATA =================
    def edit_ulasan(row):
        selected_id["id"] = row[0]
        input_ulasan.value = row[1]
        input_sentimen.value = row[2]
        input_id_pasien.value = row[4]
        page.update()

    # ================= TABEL =================
    tabel_ulasan = DataTable(
        columns=[
            DataColumn(Text("No.")),
            DataColumn(Text("Ulasan")),
            DataColumn(Text("sentimen")),
            DataColumn(Text("Tanggal")),
            DataColumn(Text("Nama Pasien")),
            DataColumn(Text("Aksi")),
        ],
        rows=[]
    )

    info_halaman = Text()

    def muat_data_ulasan():
        tabel_ulasan.rows.clear()
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()

        keyword = f"%{keyword_cari['value']}%"

        perintahSQL.execute(
            """ SELECT COUNT(*) 
                FROM riwayat_ulasan
                JOIN pasien ON riwayat_ulasan.id_pasien = pasien.id_pasien
                WHERE riwayat_ulasan.ulasan LIKE %s 
                    OR riwayat_ulasan.sentimen LIKE %s
                    OR pasien.nik_pasien LIKE %s
                    OR pasien.nama_pasien LIKE %s """,
            (keyword, keyword, keyword, keyword)
        )
        total_data["value"] = perintahSQL.fetchone()[0]

        offset = (current_page["value"] - 1) * limit_per_page

        perintahSQL.execute(
             """ SELECT 
                    riwayat_ulasan.id_riwayatulasan,
                    riwayat_ulasan.ulasan,
                    riwayat_ulasan.sentimen,
                    riwayat_ulasan.tanggal_entri,
                    riwayat_ulasan.id_pasien,
                    pasien.nik_pasien,
                    pasien.nama_pasien
                FROM riwayat_ulasan JOIN pasien ON riwayat_ulasan.id_pasien = pasien.id_pasien
                WHERE riwayat_ulasan.ulasan LIKE %s 
                OR riwayat_ulasan.sentimen LIKE %s
                OR pasien.nik_pasien LIKE %s
                OR pasien.nama_pasien LIKE %s
                ORDER BY riwayat_ulasan.id_riwayatulasan DESC
                LIMIT %s OFFSET %s """,
            (keyword, keyword, keyword, keyword, limit_per_page, offset)
        )

        for index, row in enumerate(perintahSQL.fetchall()):
            no_urut = offset + index + 1
            tabel_ulasan.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(no_urut)),
                        DataCell(Text(row[1])),
                        DataCell(Text(row[2])),
                        DataCell(Text(str(row[3]))),
                        DataCell(Text(str(row[6]))),
                        DataCell(
                            Row(
                                spacing=5,
                                controls=[
                                    IconButton(
                                        icon=Icons.EDIT,
                                        on_click=lambda e, data=row: edit_ulasan(data)
                                    ),
                                    IconButton(
                                        icon=Icons.DELETE,
                                        icon_color=Colors.RED,
                                        on_click=lambda e, id=row[0]: konfirmasi_hapus(id)
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

    # ================= PAGING =================
    def prev_page(e):
        if current_page["value"] > 1:
            current_page["value"] -= 1
            muat_data_ulasan()
            page.update()

    def next_page(e):
        total_halaman = max(1, (total_data["value"] + limit_per_page - 1) // limit_per_page)
        if current_page["value"] < total_halaman:
            current_page["value"] += 1
            muat_data_ulasan()
            page.update()

    muat_data_ulasan()

    # ================= LAYOUT =================
    form_column = Column(
        spacing=15,
        controls=[
            Text("Form Entri Ulasan", size=18, weight="bold"),
            input_ulasan,
            input_sentimen,
            input_id_pasien,
            Row([
                ElevatedButton("Simpan Data", icon=Icons.SAVE, bgcolor=Colors.TEAL, color=Colors.WHITE, on_click=simpan_ulasan),
                ElevatedButton("Batal", icon=Icons.CLEAR, bgcolor=Colors.BLACK, color=Colors.WHITE, on_click=lambda e: bersihkan_form()),
            ]),
            notif_ulasan,
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

                # TABEL
                Container(
                    expand=True,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    shadow=BoxShadow(blur_radius=20, color="black12"),
                    content=Column(
                        expand=True,
                        controls=[
                            Text("Data Riwayat Ulasan", size=18, weight="bold"),
                            input_cari,
                            Divider(),
                            Container(
                                expand=True,
                                alignment=alignment.top_left,
                                content=Row(
                                    expand=True,
                                    scroll=ScrollMode.AUTO,
                                    controls=[
                                        Column(scroll=ScrollMode.AUTO, controls=[tabel_ulasan]),
                                    ]
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
                        ],
                    ),
                ),
            ],
        ),
    )
