import flet as ft
from services.barang_service import get_list_barang, delete_barang, tambah_barang, get_satuan_dict, update_stok
from services.transaksi_service import catat_transaksi
from ai_model import predict_sales


def build_inventory_view(user):
    page_header = ft.Container(
        content=ft.Row([
            ft.Icon(name="inventory"),
            ft.Text(f"Smart Inventory - {user['username']}", size=22, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.Text(f"Hak akses: {user['hak_akses']}")
        ]),
        padding=10,
    )

    # Form tambah barang
    txt_nama = ft.TextField(label="Nama Barang")
    txt_kode = ft.TextField(label="Kode SKU")
    txt_kategori = ft.TextField(label="Kategori")
    txt_beli = ft.TextField(label="Harga Beli", keyboard_type=ft.KeyboardType.NUMBER)
    txt_jual = ft.TextField(label="Harga Jual", keyboard_type=ft.KeyboardType.NUMBER)
    txt_stok = ft.TextField(label="Stok Awal", keyboard_type=ft.KeyboardType.NUMBER)
    txt_min_stok = ft.TextField(label="Stok Minimum", keyboard_type=ft.KeyboardType.NUMBER)
    txt_satuan = ft.TextField(label="Satuan")

    def clear_form():
        for tf in [txt_nama, txt_kode, txt_kategori, txt_beli, txt_jual, txt_stok, txt_min_stok, txt_satuan]:
            tf.value = ""

    def handle_tambah(e):
        try:
            tambah_barang(
                txt_nama.value, txt_kode.value, txt_kategori.value,
                float(txt_beli.value), float(txt_jual.value),
                int(txt_stok.value), int(txt_min_stok.value), txt_satuan.value
            )
            clear_form()
            e.page.snack_bar = ft.SnackBar(ft.Text("Barang berhasil ditambahkan!"), open=True)
            load_data_table()
        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(ft.Text(f"Error Input: {ex}"), open=True, bgcolor="red")
        e.page.update()

    form_tambah = ft.AlertDialog(
        modal=True,
        title=ft.Text("Tambah Barang Baru"),
        content=ft.Column([
            txt_nama, txt_kode, txt_kategori,
            ft.Row([txt_beli, txt_jual]),
            ft.Row([txt_stok, txt_min_stok, txt_satuan])
        ], tight=True),
        actions=[
            ft.TextButton("Batal", on_click=lambda e: (setattr(form_tambah, 'open', False), e.page.update())),
            ft.ElevatedButton("Simpan", on_click=handle_tambah),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Form transaksi masuk/keluar
    tr_no = ft.TextField(label="No Faktur")
    tr_tanggal = ft.TextField(label="Tanggal (YYYY-MM-DD)")
    tr_id_barang = ft.TextField(label="ID Barang", keyboard_type=ft.KeyboardType.NUMBER)
    tr_id_supplier = ft.TextField(label="ID Supplier (opsional)")
    tr_jenis = ft.Dropdown(label="Jenis", options=[ft.dropdown.Option("masuk"), ft.dropdown.Option("keluar")])
    tr_jumlah = ft.TextField(label="Jumlah", keyboard_type=ft.KeyboardType.NUMBER)
    tr_harga = ft.TextField(label="Harga Satuan", keyboard_type=ft.KeyboardType.NUMBER)
    tr_metode = ft.TextField(label="Metode Pembayaran", value="Tunai")
    tr_ket = ft.TextField(label="Keterangan", multiline=True)

    def handle_transaksi(e):
        try:
            catat_transaksi(
                tr_no.value, tr_tanggal.value, user['id_user'], int(tr_id_barang.value),
                int(tr_id_supplier.value) if tr_id_supplier.value else None,
                tr_jenis.value, int(tr_jumlah.value), float(tr_harga.value), tr_metode.value, tr_ket.value
            )
            # Update stok
            delta = int(tr_jumlah.value) if tr_jenis.value == 'masuk' else -int(tr_jumlah.value)
            update_stok(int(tr_id_barang.value), delta)
            e.page.snack_bar = ft.SnackBar(ft.Text("Transaksi dicatat & stok diperbarui"), open=True)
            load_data_table()
        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(ft.Text(f"Error Transaksi: {ex}"), open=True, bgcolor="red")
        e.page.update()

    form_transaksi = ft.AlertDialog(
        modal=True,
        title=ft.Text("Catat Transaksi Masuk/Keluar"),
        content=ft.Column([
            tr_no, tr_tanggal,
            ft.Row([tr_id_barang, tr_id_supplier]),
            ft.Row([tr_jenis, tr_jumlah, tr_harga]),
            ft.Row([tr_metode]),
            tr_ket
        ], tight=True),
        actions=[
            ft.TextButton("Batal", on_click=lambda e: (setattr(form_transaksi, 'open', False), e.page.update())),
            ft.ElevatedButton("Simpan", on_click=handle_transaksi),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    dialog_prediksi = ft.AlertDialog(
        modal=True,
        title=ft.Text("Hasil Prediksi Stok"),
        content=ft.Text("Sedang memuat prediksi..."),
        actions=[ft.TextButton("Tutup", on_click=lambda e: (setattr(dialog_prediksi, 'open', False), e.page.update()))],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def show_prediksi(e, id_barang):
        dialog_prediksi.title = ft.Text(f"Hasil Prediksi AI - Barang ID: {id_barang}")
        dialog_prediksi.content = ft.ProgressRing()
        dialog_prediksi.open = True
        e.page.update()

        hasil_analisis = predict_sales(id_barang)

        if isinstance(hasil_analisis, str):
            content = ft.Text(hasil_analisis, color="red")
        else:
            color_bg = "green"
            if hasil_analisis['Status'].startswith("Wajib"):
                color_bg = "red"
            elif hasil_analisis['Status'].startswith("Perlu"):
                color_bg = "orange"

            satuan = get_satuan_dict().get(id_barang, {}).get('satuan_barang', 'Pcs')
            content = ft.Column([
                ft.ListTile(leading=ft.Icon(name="show_chart"), title=ft.Text("Prediksi Penjualan Mingguan:"),
                            subtitle=ft.Text(f"~{hasil_analisis['Prediksi_Mingguan']} {satuan}")),
                ft.ListTile(leading=ft.Icon(name="calendar_month"), title=ft.Text("Prediksi Penjualan Bulanan:"),
                            subtitle=ft.Text(f"~{hasil_analisis['Prediksi_Bulanan']} {satuan}")),
                ft.ListTile(leading=ft.Icon(name="inventory"), title=ft.Text("Sisa Stok Setelah Prediksi (mingguan):"),
                            subtitle=ft.Text(str(hasil_analisis['Sisa_Stok_Setelah_Prediksi']))),
                ft.Divider(),
                ft.Container(
                    ft.Text(f"STATUS INVENTORY: {hasil_analisis['Status']}", weight=ft.FontWeight.BOLD, color="white"),
                    padding=10, bgcolor=color_bg, border_radius=5
                )
            ])

        dialog_prediksi.content = content
        e.page.update()

    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nama Barang")),
            ft.DataColumn(ft.Text("Stok")),
            ft.DataColumn(ft.Text("Min Stok")),
            ft.DataColumn(ft.Text("Aksi")),
        ],
        rows=[]
    )

    def load_data_table():
        data = get_list_barang()
        rows = []
        if not data:
            rows = [ft.DataRow(cells=[
                ft.DataCell(ft.Text("-")), ft.DataCell(ft.Text("Tidak ada data")),
                ft.DataCell(ft.Text("-")), ft.DataCell(ft.Text("-")), ft.DataCell(ft.Text("-"))
            ])]
        else:
            for item in data:
                color_stok = "black"
                if item['stok_saat_ini'] <= item['stok_minimum']:
                    color_stok = "red"
                elif item['stok_saat_ini'] < item['stok_minimum'] * 1.5:
                    color_stok = "orange"
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(item['id_barang']))),
                    ft.DataCell(ft.Text(item['nama_barang'])),
                    ft.DataCell(ft.Text(str(item['stok_saat_ini']), color=color_stok, weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(str(item['stok_minimum']))),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon="analytics", tooltip="Cek Prediksi AI", on_click=lambda e, id=item['id_barang']: show_prediksi(e, id)),
                        ft.IconButton(icon="playlist_add", tooltip="Catat Transaksi", on_click=lambda e: (setattr(form_transaksi, 'open', True), e.page.update())),
                        ft.IconButton(icon="delete", tooltip="Hapus", on_click=lambda e, id=item['id_barang']: (delete_barang(id), load_data_table())),
                    ], spacing=5))
                ]))
        data_table.rows = rows

    load_data_table()

    return [
        page_header,
        ft.Row([
            ft.ElevatedButton(text="Tambah Barang", icon="add", on_click=lambda e: (setattr(form_tambah, 'open', True), setattr(e.page, 'dialog', form_tambah), e.page.update())),
            ft.ElevatedButton(text="Catat Transaksi", icon="playlist_add", on_click=lambda e: (setattr(form_transaksi, 'open', True), setattr(e.page, 'dialog', form_transaksi), e.page.update())),
        ], alignment=ft.MainAxisAlignment.END),
        ft.Divider(),
        data_table
    ], [form_tambah, form_transaksi, dialog_prediksi]
