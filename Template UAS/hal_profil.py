import pymysql
from flet import *


# =========================================================
# 🔹 koneksi database
# =========================================================
def koneksi_database():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="2025_db_mad_proyek_uas"
    )


# =========================================================
# 🔹 HALAMAN PROFIL
# =========================================================
def profil_view(page: Page, username, hak_akses):

    input_username = TextField(
        label="Username Baru",
        prefix_icon=Icons.PERSON,
        width=320
    )

    input_password = TextField(
        label="Password Baru",
        prefix_icon=Icons.LOCK,
        password=True,
        can_reveal_password=True,
        width=320
    )

    notif_profil = Text("", color=Colors.GREEN)

    # ================= SIMPAN PERUBAHAN =================
    def simpan_perubahan(e):
        if not input_username.value and not input_password.value:
            notif_profil.value = "⚠️ Username atau password harus diisi"
            notif_profil.color = Colors.RED
            page.update()
            return

        db = koneksi_database()
        cur = db.cursor()

        if input_username.value:
            cur.execute(
                "UPDATE user SET username=%s WHERE username=%s",
                (input_username.value, username)
            )

        if input_password.value:
            cur.execute(
                "UPDATE user SET password=%s WHERE username=%s",
                (input_password.value, input_username.value or username)
            )

        db.commit()
        cur.close()
        db.close()

        notif_profil.value = "✅ Profil berhasil diperbarui"
        notif_profil.color = Colors.GREEN
        page.update()

    # ================= CARD PROFIL =================
    return Container(
        alignment=alignment.top_left,
        content=Container(
            width=450,
            padding=30,
            bgcolor="white",
            border_radius=20,
            shadow=BoxShadow(blur_radius=20, color="black12"),
            content=Column(
                spacing=18,
                horizontal_alignment="center",
                controls=[
                    Icon(Icons.ACCOUNT_CIRCLE, size=90, color=Colors.BLUE),
                    Text("Profil Pengguna", size=18, weight="bold"),

                    Divider(),

                    Row(
                        alignment="center",
                        controls=[
                            Icon(Icons.BADGE),
                            Text(f"Username : {username}")
                        ]
                    ),
                    Row(
                        alignment="center",
                        controls=[
                            Icon(Icons.VERIFIED_USER),
                            Text(f"Hak Akses : {hak_akses}")
                        ]
                    ),

                    Divider(),

                    input_username,
                    input_password,

                    ElevatedButton("Simpan Perubahan", icon=Icons.SAVE, width=320, height=45, on_click=simpan_perubahan, color=Colors.WHITE, bgcolor=Colors.TEAL),

                    notif_profil
                ],
            ),
        ),
    )
