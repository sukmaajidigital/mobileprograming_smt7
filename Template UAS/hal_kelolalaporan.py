from flet import *
import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
import datetime


# ================= KONEKSI DATABASE =================
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="2025_db_mad_proyek_uas"
    )


# ================= HALAMAN KELOLA LAPORAN =================
def kelola_laporan_view(page: Page):

    # ---------- Ambil data riwayat periksa ----------
    def load_data(id_pasien_filter=None):
        conn = get_connection()
        cursor = conn.cursor()

        if id_pasien_filter:
            cursor.execute("""
                SELECT id_riwayatperiksa, imt, gula_darah, tekanan_darah,
                       diagnosis, risiko, lama_rawat, tanggal_entri, id_pasien
                FROM riwayat_periksa
                WHERE id_pasien = %s
                ORDER BY tanggal_entri DESC
            """, (id_pasien_filter,))
        else:
            cursor.execute("""
                SELECT id_riwayatperiksa, imt, gula_darah, tekanan_darah,
                       diagnosis, risiko, lama_rawat, tanggal_entri, id_pasien
                FROM riwayat_periksa
                ORDER BY tanggal_entri DESC
            """)

        rows = cursor.fetchall()
        conn.close()
        return rows

    # ---------- Refresh tabel preview ----------
    def refresh_table():
        table.rows.clear()
        data = load_data(txt_id_pasien.value)

        for row in data:
            table.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(row[0])),
                        DataCell(Text(row[1])),
                        DataCell(Text(row[2])),
                        DataCell(Text(row[3])),
                        DataCell(Text(row[4])),
                        DataCell(Text(row[5])),
                        DataCell(Text(f"{row[6]} hari")),
                        DataCell(Text(str(row[7]))),
                        DataCell(Text(row[8])),
                    ]
                )
            )
        page.update()

    # ================= CETAK PDF =================
    def cetak_laporan(e):
        data = load_data(txt_id_pasien.value)

        if not data:
            page.snack_bar = SnackBar(
                Text("⚠️ Data kosong, tidak bisa dicetak"),
                bgcolor=Colors.RED
            )
            page.snack_bar.open = True
            page.update()
            return

        file_name = "laporan_riwayat_periksa.pdf"

        pdf = SimpleDocTemplate(
            file_name,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        elements = []

        # ================= JUDUL =================
        elements.append(
            Paragraph(
                "<para align='center'><font size=18><b>SISTEM INFORMASI RIWAYAT PERIKSA</b></font></para>",
                styles["Normal"]
            )
        )
        elements.append(Paragraph("<br/>", styles["Normal"]))
        elements.append(Paragraph("<br/>", styles["Normal"]))
        
        elements.append(
            Paragraph(
                "<para align='center'><font size=13>Laporan Riwayat Periksa Pasien</font></para>",
                styles["Normal"]
            )
        )
        elements.append(Paragraph("<br/>", styles["Normal"]))

        # ================= GARIS PEMISAH =================
        elements.append(
            Table(
                [[""]],
                colWidths=[480],
                style=TableStyle([
                    ("LINEBELOW", (0, 0), (-1, -1), 1, colors.black),
                ])
            )
        )

        elements.append(Paragraph("<br/>", styles["Normal"]))

        # ================= INFO LAPORAN =================
        tanggal_cetak = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        filter_pasien = txt_id_pasien.value if txt_id_pasien.value else "Semua Pasien"

        info_table = Table(
            [
                ["Tanggal Cetak", f": {tanggal_cetak}"],
                ["Filter ID Pasien", f": {filter_pasien}"],
            ],
            colWidths=[140, 340]
        )

        info_table.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica"),
            ("FONT", (0, 0), (0, -1), "Helvetica-Bold"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))

        elements.append(info_table)
        elements.append(Paragraph("<br/><br/>", styles["Normal"]))

        # ================= TABEL DATA =================
        table_data = [[
            "ID", "IMT", "Gula Darah", "Tekanan",
            "Diagnosis", "Risiko", "Lama Rawat",
            "Tanggal", "ID Pasien"
        ]]

        for row in data:
            table_data.append([
                row[0], row[1], row[2], row[3],
                row[4], row[5],
                f"{row[6]} hari",
                str(row[7]),
                row[8]
            ])

        table_pdf = Table(table_data, repeatRows=1)

        table_pdf.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 1), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))

        elements.append(table_pdf)

        # ================= FOOTER =================
        def footer(canvas, doc):
            canvas.setFont("Helvetica", 9)
            canvas.setFillColor(colors.grey)
            canvas.drawString(
                36, 20,
                f"Dicetak oleh Aplikasi | Halaman {doc.page}"
            )
        pdf.build(elements, onFirstPage=footer, onLaterPages=footer)

        os.startfile(file_name)

        page.snack_bar = SnackBar(
            Text("✅ Laporan berhasil dicetak ke PDF"),
            bgcolor=Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()

    # ================= UI =================
    txt_id_pasien = TextField(
        label="Filter ID Pasien",
        width=220,
        prefix_icon=Icons.SEARCH
    )

    btn_filter = ElevatedButton(
        "Tampilkan",
        icon=Icons.FILTER_ALT,
        on_click=lambda e: refresh_table()
    )

    btn_cetak = ElevatedButton(
        "Cetak PDF",
        icon=Icons.PRINT,
        bgcolor=Colors.BLUE,
        color=Colors.WHITE,
        on_click=cetak_laporan
    )

    table = DataTable(
        expand=True,
        heading_row_color=Colors.BLUE_50,
        columns=[
            DataColumn(Text("ID")),
            DataColumn(Text("IMT")),
            DataColumn(Text("Gula Darah")),
            DataColumn(Text("Tekanan")),
            DataColumn(Text("Diagnosis")),
            DataColumn(Text("Risiko")),
            DataColumn(Text("Lama Rawat")),
            DataColumn(Text("Tanggal")),
            DataColumn(Text("ID Pasien")),
        ],
        rows=[]
    )

    refresh_table()

    # ================= LAYOUT =================
    return Container(
        expand=True,
        content=Column(
            spacing=15,
            controls=[
                Container(
                    padding=15,
                    bgcolor=Colors.WHITE,
                    border_radius=12,
                    shadow=BoxShadow(blur_radius=12, color=Colors.BLACK12),
                    content=Row(
                        alignment="spaceBetween",
                        controls=[
                            Row(spacing=10, controls=[txt_id_pasien, btn_filter]),
                            btn_cetak,
                        ],
                    ),
                ),
                Container(
                    expand=True,
                    padding=10,
                    bgcolor=Colors.WHITE,
                    border_radius=12,
                    shadow=BoxShadow(blur_radius=12, color=Colors.BLACK12),
                    content=table,
                ),
            ],
        ),
    )
