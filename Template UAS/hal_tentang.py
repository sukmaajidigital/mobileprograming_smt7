from flet import *


def tentang_view():
    return Container(
        alignment=alignment.top_left,
        content=Container(
            width=600,
            padding=30,
            bgcolor="white",
            border_radius=20,
            shadow=BoxShadow(blur_radius=20, color="black12"),
            content=Column(
                spacing=20,
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    # ICON & JUDUL
                    Icon(Icons.INFO_OUTLINE, size=80, color=Colors.BLUE),
                    Text(
                        "Tentang Aplikasi",
                        size=18,
                        weight=FontWeight.BOLD,
                    ),

                    Divider(),

                    # DESKRIPSI
                    Text(
                        "Aplikasi ini dikembangkan sebagai bagian dari "
                        "Proyek Ujian Akhir Semester (UAS) mata kuliah "
                        "Mobile Application Development.",
                        text_align=TextAlign.CENTER,
                        size=14,
                    ),

                    Text(
                        "Aplikasi dibangun menggunakan framework Flet "
                        "dengan bahasa pemrograman Python dan "
                        "menggunakan database MySQL sebagai backend.",
                        text_align=TextAlign.CENTER,
                        size=14,
                        color=Colors.BLACK54,
                    ),

                    Divider(),

                    # INFORMASI TEKNIS
                    Row(
                        alignment=MainAxisAlignment.CENTER,
                        spacing=30,
                        controls=[
                            _info_item(Icons.CODE, "Framework", "Flet"),
                            _info_item(Icons.STORAGE, "Database", "MySQL"),
                            _info_item(Icons.LANGUAGE, "Bahasa", "Python"),
                        ],
                    ),

                    Divider(),

                    # FOOTER
                    Text(
                        "© 2025 • Proyek UAS • Sistem Informasi",
                        size=12,
                        color=Colors.BLACK38,
                    ),
                ],
            ),
        ),
    )


# ================= HELPER =================
def _info_item(icon, title, value):
    return Column(
        spacing=5,
        horizontal_alignment=CrossAxisAlignment.CENTER,
        controls=[
            Icon(icon, size=32, color=Colors.BLUE),
            Text(title, size=12, color=Colors.BLACK54),
            Text(value, size=14, weight=FontWeight.BOLD),
        ],
    )
