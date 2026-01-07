# ================= IMPORT MODULE =================
from flet import *

# Mengimpor halaman-halaman (view) terpisah
from hal_dashboard import dashboard_view
from hal_login import login_view
from hal_profil import profil_view
from hal_tentang import tentang_view
from hal_kelolapasien import kelola_pasien_view
from hal_kelolariwayatperiksa import kelola_riwayat_periksa_view
from hal_kelolaulasan import kelola_riwayat_ulasan_view
from hal_kelolalaporan import kelola_laporan_view   # ✅ MENU BARU


# ================= FUNGSI UTAMA APLIKASI =================
def main(page: Page):
    # ---------- Konfigurasi dasar window aplikasi ----------
    page.title = "Template UAS - Flet"        # Judul aplikasi
    page.bgcolor = "#e8ecf3"                # Warna background halaman
    page.window.width = 1280                  # Lebar window
    page.window.height = 800                  # Tinggi window
    page.window.maximized = True              # Window langsung fullscreen

    # ---------- Session login ----------
    session_user = {
        "username": None,
        "hak_akses": None
    }

    # ================= HALAMAN LOGIN =================
    def tampil_hallogin():
        page.clean()
        page.add(login_view(page, tampil_halpengguna))
        page.update()

    # ================= PROSES LOGOUT =================
    def proses_logout():
        session_user["username"] = None
        session_user["hak_akses"] = None
        tampil_hallogin()

    # ================= HALAMAN UTAMA SETELAH LOGIN =================
    def tampil_halpengguna(username, hak_akses):
        session_user["username"] = username
        session_user["hak_akses"] = hak_akses

        page.clean()

        content = Column(expand=True)

        # ================= NAVIGATION RAIL =================
        rail = NavigationRail(
            selected_index=0,
            label_type=NavigationRailLabelType.ALL,
            extended=True,
            destinations=[
                NavigationRailDestination(icon=Icons.HOME, label="Beranda"),
                NavigationRailDestination(icon=Icons.PEOPLE, label="Kelola Pasien"),
                NavigationRailDestination(icon=Icons.MEDICAL_SERVICES, label="Riwayat Periksa"),
                NavigationRailDestination(icon=Icons.COMMENT, label="Riwayat Ulasan"),
                NavigationRailDestination(icon=Icons.DESCRIPTION, label="Kelola Laporan"),  # ✅ BARU
                NavigationRailDestination(icon=Icons.PERSON, label="Profil"),
                NavigationRailDestination(icon=Icons.INFO, label="Tentang"),
                NavigationRailDestination(icon=Icons.LOGOUT, label="Logout"),
            ],
        )

        # ================= EVENT SAAT MENU DIKLIK =================
        def change(e):
            content.controls.clear()

            # ---------- Dashboard ----------
            if rail.selected_index == 0:
                content.controls.append(
                    Column(
                        spacing=10,
                        expand=True,
                        controls=[
                            Text(
                                f"👋 Selamat datang, {session_user['username']} "
                                f"({session_user['hak_akses']})",
                                size=18,
                                weight="bold",
                            ),
                            dashboard_view(),
                        ],
                    )
                )

            # ---------- Kelola Pasien ----------
            elif rail.selected_index == 1:
                content.controls.append(
                    Column(
                        spacing=10,
                        expand=True,
                        controls=[
                            Text("💻 Halaman Kelola Pasien", size=18, weight="bold"),
                            kelola_pasien_view(page),
                        ],
                    )
                )

            # ---------- Riwayat Periksa ----------
            elif rail.selected_index == 2:
                content.controls.append(
                    Column(
                        spacing=10,
                        expand=True,
                        controls=[
                            Text("💻 Halaman Kelola Periksa", size=18, weight="bold"),
                            kelola_riwayat_periksa_view(page),
                        ],
                    )
                )

            # ---------- Riwayat Ulasan ----------
            elif rail.selected_index == 3:
                content.controls.append(
                    Column(
                        spacing=10,
                        expand=True,
                        controls=[
                            Text("💻 Halaman Kelola Ulasan", size=18, weight="bold"),
                            kelola_riwayat_ulasan_view(page),
                        ],
                    )
                )

            # ---------- Kelola Laporan ----------
            elif rail.selected_index == 4:
                content.controls.append(
                    Column(
                        spacing=10,
                        expand=True,
                        controls=[
                            Text("💻 Halaman Kelola Laporan", size=18, weight="bold"),
                            kelola_laporan_view(page),
                        ],
                    )
                )

            # ---------- Profil ----------
            elif rail.selected_index == 5:
                content.controls.append(
                    profil_view(
                        page,
                        session_user["username"],
                        session_user["hak_akses"]
                    )
                )

            # ---------- Tentang ----------
            elif rail.selected_index == 6:
                content.controls.append(tentang_view())

            # ---------- Logout ----------
            elif rail.selected_index == 7:
                content.controls.append(
                    Container(
                        alignment=alignment.center,
                        content=Container(
                            width=420,
                            padding=25,
                            bgcolor=Colors.WHITE,
                            border_radius=16,
                            shadow=BoxShadow(
                                blur_radius=20,
                                color=Colors.BLACK12,
                            ),
                            content=Column(
                                horizontal_alignment="center",
                                spacing=20,
                                controls=[
                                    Icon(Icons.LOGOUT, size=60, color=Colors.RED_400),
                                    Text("Konfirmasi Logout", size=22, weight="bold"),
                                    Text(
                                        "Apakah Anda yakin ingin keluar dari aplikasi?",
                                        text_align="center",
                                        color=Colors.GREY_700
                                    ),
                                    Row(
                                        alignment="spaceEvenly",
                                        controls=[
                                            OutlinedButton(
                                                "Batal",
                                                icon=Icons.CLOSE,
                                                on_click=lambda e: (
                                                    setattr(rail, "selected_index", 0),
                                                    change(None)
                                                ),
                                            ),
                                            ElevatedButton(
                                                "Logout",
                                                icon=Icons.LOGOUT,
                                                bgcolor=Colors.RED,
                                                color=Colors.WHITE,
                                                on_click=lambda e: proses_logout(),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                    )
                )

            page.update()

        rail.on_change = change

        # ================= LAYOUT UTAMA =================
        page.add(
            Row(
                expand=True,
                spacing=12,
                controls=[
                    # ---------- SIDEBAR ----------
                    Container(
                        width=260,
                        padding=12,
                        bgcolor=Colors.WHITE,
                        border_radius=12,
                        shadow=BoxShadow(
                            blur_radius=12,
                            color=Colors.BLACK12,
                        ),
                        content=Column(
                            spacing=18,
                            controls=[
                                Column(
                                    horizontal_alignment="center",
                                    spacing=8,
                                    controls=[
                                        Container(
                                            width=80,
                                            height=80,
                                            border_radius=40,
                                            bgcolor=Colors.BLUE_100,
                                            alignment=alignment.center,
                                            content=Icon(Icons.PERSON, size=46),
                                        ),
                                        Text(session_user["username"], weight="bold"),
                                        Text(
                                            session_user["hak_akses"],
                                            size=12,
                                            color=Colors.GREY_600,
                                        ),
                                        Divider(),
                                    ],
                                ),
                                Container(
                                    height=page.height - 220,
                                    content=rail,
                                ),
                            ],
                        ),
                    ),

                    # ---------- AREA KONTEN ----------
                    Container(
                        expand=True,
                        padding=15,
                        content=content,
                    ),
                ],
            )
        )

        change(None)

    # ================= START APLIKASI =================
    tampil_hallogin()


# Menjalankan aplikasi Flet
app(main)
