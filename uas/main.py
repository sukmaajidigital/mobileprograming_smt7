# main.py (FINAL FIX - STRING ICONS & COLORS)

import flet as ft
from koneksi import fetch_data, execute_query
from ai_model import predict_sales

# --- 1. Fungsi CRUD ---

def get_list_barang():
    """Mengambil semua data barang."""
    return fetch_data("SELECT id_barang, nama_barang, stok_saat_ini, harga_jual, stok_minimum FROM barang")

def delete_barang(id_barang):
    """Menghapus barang berdasarkan ID."""
    query = "DELETE FROM barang WHERE id_barang = %s"
    return execute_query(query, (id_barang,))

def tambah_barang(nama, kode, kategori, beli, jual, stok, min_stok, satuan):
    """Menambahkan barang baru."""
    query = """
    INSERT INTO barang (nama_barang, kode_sku, kategori, harga_beli, harga_jual, stok_saat_ini, stok_minimum, satuan_barang) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (nama, kode, kategori, beli, jual, stok, min_stok, satuan)
    return execute_query(query, params)

# --- 2. Fungsi Utama Aplikasi Flet ---

def main(page: ft.Page):
    page.title = "Smart Inventory Flet - Prediksi Stok"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT

    # Dialog untuk Tambah Barang
    
    txt_nama = ft.TextField(label="Nama Barang")
    txt_kode = ft.TextField(label="Kode SKU")
    txt_kategori = ft.TextField(label="Kategori")
    txt_beli = ft.TextField(label="Harga Beli", keyboard_type=ft.KeyboardType.NUMBER)
    txt_jual = ft.TextField(label="Harga Jual", keyboard_type=ft.KeyboardType.NUMBER)
    txt_stok = ft.TextField(label="Stok Awal", keyboard_type=ft.KeyboardType.NUMBER)
    txt_min_stok = ft.TextField(label="Stok Minimum", keyboard_type=ft.KeyboardType.NUMBER)
    txt_satuan = ft.TextField(label="Satuan")
    
    def clear_form():
        txt_nama.value = txt_kode.value = txt_kategori.value = txt_beli.value = ""
        txt_jual.value = txt_stok.value = txt_min_stok.value = txt_satuan.value = ""
        page.update()

    def handle_tambah(e):
        try:
            tambah_barang(
                txt_nama.value, txt_kode.value, txt_kategori.value, 
                float(txt_beli.value), float(txt_jual.value), 
                int(txt_stok.value), int(txt_min_stok.value), txt_satuan.value
            )
            clear_form()
            dlg_tambah.open = False
            page.snack_bar = ft.SnackBar(ft.Text("Barang berhasil ditambahkan!"), open=True)
            load_data_table()
            page.update()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error Input: {ex}"), open=True, bgcolor="red")
            page.update()

    dlg_tambah = ft.AlertDialog(
        modal=True,
        title=ft.Text("Tambah Barang Baru"),
        content=ft.Column([
            txt_nama, txt_kode, txt_kategori, 
            ft.Row([txt_beli, txt_jual]), 
            ft.Row([txt_stok, txt_min_stok, txt_satuan])
        ], tight=True),
        actions=[
            ft.TextButton("Batal", on_click=lambda e: (setattr(dlg_tambah, 'open', False), page.update())),
            ft.ElevatedButton("Simpan", on_click=handle_tambah),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Menampilkan Dialog Prediksi AI
    
    dialog_prediksi = ft.AlertDialog(
        modal=True,
        title=ft.Text("Hasil Prediksi Stok"),
        content=ft.Text("Sedang memuat prediksi..."),
        actions=[ft.TextButton("Tutup", on_click=lambda e: (setattr(dialog_prediksi, 'open', False), page.update()))],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    def show_prediksi(e, id_barang):
        dialog_prediksi.title = ft.Text(f"Hasil Prediksi AI - Barang ID: {id_barang}")
        dialog_prediksi.content = ft.ProgressRing() # Tampilkan loading
        dialog_prediksi.open = True
        page.update()

        # Integrasi AI: Panggil fungsi prediksi dari ai_model.py
        hasil_analisis = predict_sales(id_barang)
        
        # Format hasil prediksi ke UI Flet
        if isinstance(hasil_analisis, str): # Jika error/data kurang
             content = ft.Text(hasil_analisis, color="red")
        else:
            color_bg = "green"
            if hasil_analisis['Status'].startswith("Wajib"):
                color_bg = "red"
            elif hasil_analisis['Status'].startswith("Perlu"):
                color_bg = "orange"

            # FIX: Menggunakan string untuk nama icon (misal: "insights", "inventory")
            content = ft.Column([
                ft.ListTile(leading=ft.Icon(name="insights"), title=ft.Text("Prediksi Penjualan Mingguan:"), 
                            subtitle=ft.Text(f"~{hasil_analisis['Prediksi_Mingguan']} {get_list_barang_dict().get(id_barang, {}).get('satuan_barang', 'Pcs')}")),
                ft.ListTile(leading=ft.Icon(name="inventory"), title=ft.Text("Stok Tersisa Setelah Prediksi:"), 
                            subtitle=ft.Text(str(hasil_analisis['Sisa_Stok_Setelah_Prediksi']))),
                ft.Divider(),
                ft.Container(
                    ft.Text(f"STATUS INVENTORY: {hasil_analisis['Status']}", weight=ft.FontWeight.BOLD, color="white"),
                    padding=10, bgcolor=color_bg, border_radius=5
                )
            ])
            
        dialog_prediksi.content = content
        page.update()
        
    # Fungsi untuk mendapatkan data barang (digunakan untuk memuat tabel)
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
    
    # Fungsi pembantu untuk mendapatkan satuan (untuk UI Prediksi)
    def get_list_barang_dict():
        barang_list = fetch_data("SELECT id_barang, satuan_barang FROM barang")
        return {item['id_barang']: item for item in barang_list}

    def load_data_table():
        data = get_list_barang()
        
        if not data:
            data_table.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("-")),
                    ft.DataCell(ft.Text("Tidak ada data")),
                    ft.DataCell(ft.Text("-")),
                    ft.DataCell(ft.Text("-")),
                    ft.DataCell(ft.Text("-")),
                ])
            ]
            page.update()
            return

        rows = []
        for item in data:
            # Tentukan warna stok
            color_stok = "black"
            if item['stok_saat_ini'] <= item['stok_minimum']:
                color_stok = "red"
            elif item['stok_saat_ini'] < item['stok_minimum'] * 1.5:
                color_stok = "orange"
            
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(item['id_barang']))),
                        ft.DataCell(ft.Text(item['nama_barang'])),
                        ft.DataCell(ft.Text(str(item['stok_saat_ini']), color=color_stok, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(item['stok_minimum']))),
                        ft.DataCell(
                            ft.Row([
                                # FIX: Icon diganti string "analytics" dan "delete"
                                ft.IconButton(icon="analytics", tooltip="Cek Prediksi AI", on_click=lambda e, id=item['id_barang']: show_prediksi(e, id)),
                                ft.IconButton(icon="delete", tooltip="Hapus", on_click=lambda e, id=item['id_barang']: (delete_barang(id), load_data_table())),
                            ], spacing=5)
                        ),
                    ]
                )
            )
        data_table.rows = rows
        page.update()

    # --- Tampilan UI Utama ---
    
    page.dialog = dlg_tambah
    page.overlay.append(dialog_prediksi)

    page.add(
        ft.Container(
            content=ft.Text("Smart Inventory & Prediksi Stok Barang", size=24, weight=ft.FontWeight.BOLD),
            padding=10
        ),
        ft.Row([
            ft.ElevatedButton(
                text="Tambah Barang (CRUD)",
                # FIX: Icon diganti string "add"
                icon="add",
                on_click=lambda e: (setattr(dlg_tambah, 'open', True), page.update())
            ),
        ], alignment=ft.MainAxisAlignment.END),
        ft.Divider(),
        ft.Container(
            content=data_table,
            expand=True,
            padding=ft.padding.only(bottom=20)
        )
    )

    # Muat data saat aplikasi pertama kali dijalankan
    load_data_table()


if __name__ == "__main__":
    ft.app(target=main)