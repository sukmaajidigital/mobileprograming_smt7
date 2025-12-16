import flet as ft
from db_ai_service import get_all_barang, predict_stok_habis, calculate_moving_average_sales
from db_ai_service import update_stok, connect_db
import pandas as pd

def main(page: ft.Page):
    page.title = "Flet Smart Inventory (AI Prediction)"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 1200
    page.window_height = 800
    
    # --- UI Components ---
    
    # Data Table untuk menampilkan data barang
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nama Barang")),
            ft.DataColumn(ft.Text("Kategori")),
            ft.DataColumn(ft.Text("Harga Jual")),
            ft.DataColumn(ft.Text("Stok")),
            ft.DataColumn(ft.Text("Min Stok")),
            ft.DataColumn(ft.Text("MA Penjualan")),
            ft.DataColumn(ft.Text("Prediksi Stok Habis")),
            ft.DataColumn(ft.Text("Aksi")),
        ],
        rows=[]
    )
    
    # Teks output prediksi (di luar tabel)
    prediksi_output = ft.Text("Pilih barang untuk melihat prediksi AI.", size=16, weight=ft.FontWeight.BOLD)
    
    # Popup Dialog (untuk aksi Jual/Kurangi Stok)
    dlg_input = ft.AlertDialog(
        modal=True,
        title=ft.Text("Input Transaksi Keluar (Penjualan)"),
        content=ft.Column([
            ft.Text("Barang Terpilih: "),
            ft.TextField(label="Jumlah Dijual", value="1", width=150, input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]")),
        ], tight=True),
        actions=[
            ft.TextButton("Batal", on_click=lambda e: close_dlg(e)),
            ft.ElevatedButton("Jual", on_click=lambda e: submit_jual(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("Dialog ditutup!"),
    )
    
    # --- Logika & Fungsi ---
    
    selected_barang_id = None
    selected_barang_name = ""
    
    def close_dlg(e):
        dlg_input.open = False
        page.update()

    def submit_jual(e):
        """Menjalankan logika penjualan (Kurangi Stok) dan update UI."""
        global selected_barang_id
        
        qty_jual = int(dlg_input.content.controls[1].value)
        
        if selected_barang_id and qty_jual > 0:
            # 1. Update Stok di DB
            if update_stok(selected_barang_id, qty_jual, 'keluar'):
                # 2. Tutup dialog dan muat ulang data
                close_dlg(e)
                load_data()
                page.snack_bar = ft.SnackBar(ft.Text(f"Berhasil menjual {qty_jual} unit {selected_barang_name}!"), open=True)
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Gagal update stok (Mungkin stok tidak cukup)!"), open=True)

        page.update()

    def open_jual_dlg(e):
        """Menyiapkan dan menampilkan dialog penjualan."""
        global selected_barang_id, selected_barang_name
        
        # Ambil data dari tombol
        selected_barang_id = e.control.data['id_barang']
        selected_barang_name = e.control.data['nama_barang']
        
        # Update teks di dialog
        dlg_input.content.controls[0].value = f"Barang Terpilih: {selected_barang_name}"
        page.dialog = dlg_input
        dlg_input.open = True
        page.update()

    def run_ai_prediction(e):
        """Menjalankan fungsi prediksi AI dan mengupdate output."""
        id_barang = e.control.data['id_barang']
        nama_barang = e.control.data['nama_barang']
        
        # Panggil fungsi AI dari helper
        status, date_prediksi, ma_sales, predicted_daily_sales = predict_stok_habis(id_barang)
        
        if status == "Prediksi Sukses":
            output_text = (
                f"**Analisis AI untuk {nama_barang} (ID: {id_barang}):**\n"
                f" - Rata-rata Penjualan (Moving Average 7 Hari): **{ma_sales} unit/hari**\n"
                f" - Penjualan Harian Diprediksi (Model Regresi): **{predicted_daily_sales} unit/hari**\n"
                f" - **Tanggal Prediksi Stok Habis:** **{date_prediksi}**\n"
                f" *Rekomendasi: Lakukan Restock sebelum tanggal tersebut.*"
            )
            prediksi_output.value = output_text
        else:
            prediksi_output.value = f"Gagal menjalankan Prediksi AI: {status}. Cek minimal 5 data penjualan untuk barang ini."
            
        page.update()


    def load_data():
        """Mengambil data dari DB dan mengisi Data Table."""
        
        # Cek koneksi DB dulu
        if not connect_db():
            data_table.rows = [ft.DataRow(cells=[ft.DataCell(ft.Text("Error Koneksi Database!")), ft.DataCell(ft.Text("")), ft.DataCell(ft.Text(""))])]
            page.update()
            return
            
        barang_list = get_all_barang()
        
        new_rows = []
        for barang in barang_list:
            # Panggil AI/Metode Pengolahan Data untuk setiap barang (hanya untuk Moving Average)
            # Prediksi penuh akan dipanggil saat tombol AI di-klik
            # Untuk demo, kita skip MA karena perlu query penjualan, kita pakai 0 dulu
            # ma_sales_val = calculate_moving_average_sales(df_penjualan_barang_x) 
            ma_sales_val = "N/A" # Skip MA di sini agar loading cepat
            
            # Baris Data Table
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(barang['id_barang']))),
                    ft.DataCell(ft.Text(barang['nama_barang'])),
                    ft.DataCell(ft.Text(barang['kategori'])),
                    ft.DataCell(ft.Text(f"Rp {barang['harga_jual']:,}")),
                    ft.DataCell(ft.Text(str(barang['stok_saat_ini']), weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(str(barang['stok_minimum']))),
                    ft.DataCell(ft.Text(ma_sales_val)),
                    ft.DataCell(
                        ft.ElevatedButton(
                            "Run AI Prediksi", 
                            data=barang, 
                            on_click=run_ai_prediction,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE_GREY_500, 
                                color=ft.colors.WHITE
                            )
                        )
                    ),
                    ft.DataCell(
                        ft.ElevatedButton(
                            "Jual", 
                            icon=ft.icons.REMOVE,
                            data=barang, 
                            on_click=open_jual_dlg
                        )
                    ),
                ]
            )
            new_rows.append(row)
            
        data_table.rows = new_rows
        page.update()

    # --- Layout Utama ---
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("Dashboard Smart Inventory", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Mengelola Stok dan Memprediksi Kebutuhan Restock dengan AI.", size=14, italic=True),
                    ft.Divider(),
                    
                    # Section Prediksi AI
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Hasil Analisis & Prediksi (Integrasi AI)", size=18, weight=ft.FontWeight.BOLD),
                                    prediksi_output
                                ],
                                spacing=10
                            ),
                            padding=20,
                        ),
                        margin=10
                    ),
                    
                    ft.Divider(),

                    # Section Data Barang & CRUD
                    ft.Row(
                        [
                            ft.Text("Master Data Barang", size=20, weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                "Refresh Data", 
                                icon=ft.icons.REFRESH, 
                                on_click=lambda e: load_data()
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    
                    ft.Container(
                        content=ft.Row([data_table], scroll=ft.ScrollMode.AUTO),
                        padding=10
                    ),
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            padding=20,
        )
    )
    
    # Muat data saat aplikasi pertama kali dijalankan
    load_data()

ft.app(target=main)