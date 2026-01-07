import pymysql
from flet import *
from datetime import datetime
from threading import Timer


# =========================================================
# 🔹 koneksi ke Database
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "2025_db_mad_proyek_uas"
    )



def login_view(page: Page, on_login_success):
    inputan_username = TextField(label="Username", width=300)
    inputan_password = TextField(label="Password", password=True, width=300)
    notif_login = Text("", color = Colors.RED)

    # 🔘 Fungsi Loading
    def tampil_loading(text=""):
        page.clean()
        page.add(
            Container(
                alignment=alignment.center,
                content=Container(
                    padding=30,
                    margin=margin.only(top=300),  # ⬅️ padding atas (800 / 4)
                    bgcolor="white",
                    border_radius=20,
                    shadow=BoxShadow(blur_radius=20, color="black12"),
                    content=Column(
                        spacing=15,
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        controls=[
                            ProgressRing(width=60, height=60),
                            Text(text, size=16, weight=FontWeight.BOLD),
                            ],
                    ),
                )
                    
            )
        )
        page.update()



    def proses_login(e):
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
            Timer(1, lambda: on_login_success(v_username, v_hak_akses)).start()
        
        # validasi jika user tidak ada
        else:
            notif_login.value = "❌ Username atau password salah!"
            page.update()
            def bersihkan_notif():
                notif_login.value = ""
                page.update()
            # Hilangkan notifikasi otomatis setelah 2 detik
            Timer(2, bersihkan_notif).start()

    login_card = Container(
        width=420,
        padding=30,
        height=400,
        bgcolor="white",
        border_radius=20,
        shadow=BoxShadow(blur_radius=20, color="black12"),
        content=Column(
            horizontal_alignment="center",
            spacing=15,
            controls=[
                Text("🔐", size=50, weight="bold"),
                Text("Proyek UAS", size=28, weight="bold"),
                inputan_username,
                inputan_password,
                ElevatedButton("Log In ➡️", width=300, height=50, on_click=proses_login, color=Colors.WHITE, bgcolor=Colors.TEAL),
                notif_login
            ],
        ),
    )

    return Container(
        expand=True,
        alignment=alignment.center,
        content=login_card,
    )
