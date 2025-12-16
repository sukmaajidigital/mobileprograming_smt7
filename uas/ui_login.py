import flet as ft
from koneksi import fetch_data


def build_login_view(on_success):
    username = ft.TextField(label="Username")
    password = ft.TextField(label="Password", password=True, can_reveal_password=True)
    info = ft.Text(value="", color="red")

    def try_login(e):
        rows = fetch_data(
            "SELECT id_user, username, hak_akses FROM user WHERE username = %s AND password = %s",
            (username.value, password.value),
        )
        if rows:
            info.value = ""
            on_success(rows[0])
        else:
            info.value = "Username/Password salah"
        e.page.update()

    return ft.Column([
        ft.Text("Login Sistem Inventory", size=22, weight=ft.FontWeight.BOLD),
        username,
        password,
        ft.Row([
            ft.ElevatedButton("Masuk", icon="login", on_click=try_login),
        ], alignment=ft.MainAxisAlignment.END),
        info,
    ], tight=True)
