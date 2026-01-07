import pymysql
from flet import *


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
# 🔹 HALAMAN KELOLA RIWAYAT PERIKSA PASIEN
# =========================================================
def kelola_riwayat_periksa_view(page: Page):

    selected_id = {"id": None}

    # ================= PAGINATION & SEARCH STATE =================
    current_page = {"value": 1}
    limit_per_page = 10
    total_data = {"value": 0}
    keyword_cari = {"value": ""}

    # ================= FORM INPUT =================
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
    
    def buat_dropdown_risiko():
        return Dropdown(
            label="Risiko",
            options=[
                dropdown.Option("Rendah"),
                dropdown.Option("Sedang"),
                dropdown.Option("Tinggi"),
            ],
            prefix_icon=Icons.WARNING,
            width=360,
        )

    input_id_pasien = buat_dropdown_pasien()

    input_imt = TextField(label="IMT", prefix_icon=Icons.MONITOR_WEIGHT, width=360)
    input_gula_darah = TextField(label="Gula Darah", prefix_icon=Icons.BLOODTYPE, width=360)
    input_tekanan_darah = TextField(label="Tekanan Darah", prefix_icon=Icons.FAVORITE, width=360)
    input_diagnosis = TextField(label="Diagnosis", prefix_icon=Icons.MEDICAL_INFORMATION, width=360)
    input_risiko = buat_dropdown_risiko()
    input_lama_rawat = TextField(label="Lama Rawat (Hari)", prefix_icon=Icons.TIMER, width=360)

    notif_riwayat = Text("")

    # ================= INPUT SEARCH =================
    input_cari = TextField(
        hint_text="Cari nama / diagnosis / risiko...",
        prefix_icon=Icons.SEARCH,
        on_change=lambda e: proses_cari(e),
        width=350
    )

    # ================= RESET FORM =================
    def bersihkan_form():
        nonlocal input_id_pasien, input_risiko
        input_imt.value = ""
        input_gula_darah.value = ""
        input_tekanan_darah.value = ""
        input_diagnosis.value = ""
        input_risiko.value = None
        input_lama_rawat.value = ""
        selected_id["id"] = None
        # 🔥 Reset dropdown pasien
        dropdown_pasien_baru = buat_dropdown_pasien()
        idx_pasien = form_column.controls.index(input_id_pasien)
        form_column.controls[idx_pasien] = dropdown_pasien_baru
        input_id_pasien = dropdown_pasien_baru
        # 🔥 Reset dropdown risiko (INI FIX UTAMA)
        dropdown_risiko_baru = buat_dropdown_risiko()
        idx_risiko = form_column.controls.index(input_risiko)
        form_column.controls[idx_risiko] = dropdown_risiko_baru
        input_risiko = dropdown_risiko_baru
        page.update()


    # ================= PROSES SEARCH =================
    def proses_cari(e):
        keyword_cari["value"] = e.control.value
        current_page["value"] = 1
        muat_data_riwayat()
        page.update()

    # ================= SIMPAN / UPDATE =================
    def simpan_riwayat(e):
        if not input_id_pasien.value or not input_diagnosis.value or not input_risiko.value:
            notif_riwayat.value = "❌ Data wajib diisi"
            notif_riwayat.color = Colors.RED
            page.update()
            return

        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()

        if selected_id["id"]:  # UPDATE
            perintahSQL.execute(
                """ UPDATE riwayat_periksa SET 
                    imt=%s, gula_darah=%s, tekanan_darah=%s,
                    diagnosis=%s, risiko=%s, lama_rawat=%s
                    WHERE id_riwayatperiksa=%s """,
                (
                    input_imt.value,
                    input_gula_darah.value,
                    input_tekanan_darah.value,
                    input_diagnosis.value,
                    input_risiko.value,
                    input_lama_rawat.value,
                    selected_id["id"],
                ),
            )
            notif_riwayat.value = "✅ Data diperbarui"
        else:  # INSERT
            perintahSQL.execute(
                """ INSERT INTO riwayat_periksa
                    (imt, gula_darah, tekanan_darah, diagnosis, risiko, lama_rawat, tanggal_entri, id_pasien)
                    VALUES (%s,%s,%s,%s,%s,%s,NOW(),%s) """,
                (
                    input_imt.value,
                    input_gula_darah.value,
                    input_tekanan_darah.value,
                    input_diagnosis.value,
                    input_risiko.value,
                    input_lama_rawat.value,
                    input_id_pasien.value,
                ),
            )
            notif_riwayat.value = "✅ Data ditambahkan"

        buka_koneksi.commit()
        perintahSQL.close()
        buka_koneksi.close()

        notif_riwayat.color = Colors.GREEN
        bersihkan_form()
        muat_data_riwayat()
        page.update()

    # ================= KONFIRMASI HAPUS =================
    def konfirmasi_hapus(id_data):
        dialog = AlertDialog(
            modal=True,
            title=Text("Konfirmasi"),
            content=Text("Yakin ingin menghapus data ini?"),
            actions=[
                TextButton("Batal", on_click=lambda e: page.close(dialog)),
                ElevatedButton(
                    "Hapus",
                    bgcolor=Colors.RED,
                    color=Colors.WHITE,
                    on_click=lambda e: hapus_riwayat(dialog, id_data),
                ),
            ],
        )
        page.open(dialog)

    def hapus_riwayat(dialog, id_data):
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()
        perintahSQL.execute(
            "DELETE FROM riwayat_periksa WHERE id_riwayatperiksa=%s",
            (id_data,),
        )
        buka_koneksi.commit()
        perintahSQL.close()
        buka_koneksi.close()

        page.close(dialog)
        bersihkan_form()
        muat_data_riwayat()
        page.update()

    # ================= EDIT =================
    def edit_riwayat(row):
        selected_id["id"] = row[0]
        input_id_pasien.value = str(row[1])
        input_imt.value = row[2]
        input_gula_darah.value = row[3]
        input_tekanan_darah.value = row[4]
        input_diagnosis.value = row[5]
        input_risiko.value = row[6]
        input_lama_rawat.value = row[7]
        page.update()

    # ================= TABEL =================
    tabel_riwayat = DataTable(
        columns=[
            DataColumn(Text("No.")),
            DataColumn(Text("Nama Pasien")),
            DataColumn(Text("IMT")),
            DataColumn(Text("Gula Darah")),
            DataColumn(Text("Tekanan Darah")),
            DataColumn(Text("Diagnosis")),
            DataColumn(Text("Risiko")),
            DataColumn(Text("Lama Rawat")),
            DataColumn(Text("Tanggal")),
            DataColumn(Text("Aksi")),
        ],
        rows=[],
    )

    info_halaman = Text()

    def muat_data_riwayat():
        tabel_riwayat.rows.clear()
        buka_koneksi = koneksi_database()
        perintahSQL = buka_koneksi.cursor()

        keyword = f"%{keyword_cari['value']}%"

        perintahSQL.execute(
            """ SELECT COUNT(*) FROM riwayat_periksa JOIN pasien ON riwayat_periksa.id_pasien = pasien.id_pasien
                WHERE riwayat_periksa.diagnosis LIKE %s OR riwayat_periksa.risiko LIKE %s OR pasien.nama_pasien LIKE %s """,
            (keyword, keyword, keyword),
        )
        total_data["value"] = perintahSQL.fetchone()[0]

        offset = (current_page["value"] - 1) * limit_per_page

        perintahSQL.execute(
            """ SELECT 
                    riwayat_periksa.id_riwayatperiksa, riwayat_periksa.id_pasien, riwayat_periksa.imt, 
                    riwayat_periksa.gula_darah, riwayat_periksa.tekanan_darah, riwayat_periksa.diagnosis, riwayat_periksa.risiko, 
                    riwayat_periksa.lama_rawat, riwayat_periksa.tanggal_entri, pasien.nama_pasien
                FROM riwayat_periksa JOIN pasien ON riwayat_periksa.id_pasien = pasien.id_pasien
                WHERE riwayat_periksa.diagnosis LIKE %s OR riwayat_periksa.risiko LIKE %s OR pasien.nama_pasien LIKE %s
                ORDER BY riwayat_periksa.id_riwayatperiksa DESC
                LIMIT %s OFFSET %s """,
            (keyword, keyword, keyword, limit_per_page, offset),
        )

        for index, row in enumerate(perintahSQL.fetchall()):
            no_urut = offset + index + 1
            tabel_riwayat.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(no_urut)),
                        DataCell(Text(f"{row[1]} # {row[9]}")),
                        DataCell(Text(row[2])),
                        DataCell(Text(row[3])),
                        DataCell(Text(row[4])),
                        DataCell(Text(row[5])),
                        DataCell(Text(row[6])),
                        DataCell(Text(f"{row[7]} hari")),
                        DataCell(Text(str(row[8]))),
                        DataCell(
                            Row(
                                spacing=5,
                                controls=[
                                    IconButton(
                                        icon=Icons.EDIT,
                                        on_click=lambda e, data=row: edit_riwayat(data),
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

    # ================= PAGING =================
    def prev_page(e):
        if current_page["value"] > 1:
            current_page["value"] -= 1
            muat_data_riwayat()
            page.update()

    def next_page(e):
        total_halaman = max(1, (total_data["value"] + limit_per_page - 1) // limit_per_page)
        if current_page["value"] < total_halaman:
            current_page["value"] += 1
            muat_data_riwayat()
            page.update()

    muat_data_riwayat()

    # ================= LAYOUT =================
    form_column = Column(
        spacing=15,
        controls=[
            Text("Form Entri", size=18, weight="bold"),
            input_id_pasien,
            input_imt,
            input_gula_darah,
            input_tekanan_darah,
            input_diagnosis,
            input_risiko,
            input_lama_rawat,
            Row([
                ElevatedButton("Simpan", icon=Icons.SAVE, bgcolor=Colors.TEAL, color=Colors.WHITE, on_click=simpan_riwayat),
                ElevatedButton("Batal", icon=Icons.CLEAR, bgcolor=Colors.BLACK, color=Colors.WHITE, on_click=lambda e: bersihkan_form()),
            ]),
            notif_riwayat,
        ],
    )

    return Container(
        expand=True,
        padding=20,
        content=Row(
            spacing=20,
            controls=[
                Container(
                    width=380,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    shadow=BoxShadow(blur_radius=20, color="black12"),
                    content=form_column
                ),

                Container(
                    expand=True,
                    padding=20,
                    bgcolor="white",
                    border_radius=20,
                    shadow=BoxShadow(blur_radius=20, color="black12"),
                    content=Column(
                        expand=True,
                        controls=[
                            Text("Data Riwayat Periksa", size=18, weight="bold"),
                            input_cari,
                            Divider(),
                            Container(
                                expand=True,
                                alignment=alignment.top_left,
                                content=Row(
                                    expand=True,
                                    scroll=ScrollMode.AUTO,
                                    controls=[
                                        Column(scroll=ScrollMode.AUTO, controls=[tabel_riwayat]),
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
                        ]
                    ),
                ),
            ],
        ),
    )
