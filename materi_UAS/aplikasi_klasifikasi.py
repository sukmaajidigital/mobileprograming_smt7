from flet import *
import pandas as pd
import numpy as np
import os

from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier


def main(page: Page):
    page.title = "Klasifikasi Penjualan"
    page.bgcolor = Colors.GREY_100
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # ================= LOAD DATA =================
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "data_train_penjualan.xlsx")

    if not os.path.exists(file_path):
        raise FileNotFoundError("❌ File data_train_penjualan.xlsx tidak ditemukan")

    df = pd.read_excel(file_path)

    X = df[["rata_penjualan"]]
    y = df["kategori"]

    # ================= MODEL =================
    model_nb = GaussianNB().fit(X, y)
    model_knn = KNeighborsClassifier(n_neighbors=3).fit(X, y)
    model_svm = SVC(kernel="linear").fit(X, y)
    model_ann = MLPClassifier(
        hidden_layer_sizes=(16, 8),
        max_iter=2000
    ).fit(X, y)

    # ================= LSTM (SIMULASI) =================
    def lstm_predict(nilai):
        if nilai < 300:
            return "Rendah"
        elif nilai < 600:
            return "Sedang"
        else:
            return "Tinggi"

    # ================= INPUT =================
    input_penjualan = TextField(
        label="Rata-rata Penjualan",
        keyboard_type=KeyboardType.NUMBER,
        width=320,
        border_radius=12,
    )

    # ================= RADIO METODE =================
    radio_metode = RadioGroup(
        value="Naive Bayes",
        content=Column(
            spacing=8,
            controls=[
                Text("Algoritma Klasifikasi", weight="bold", size=14),
                Divider(),
                Text("Machine Learning (Traditional)", weight="bold", size=14),
                Radio(value="Naive Bayes", label="Naive Bayes"),
                Radio(value="KNN", label="K-Nearest Neighbor (KNN)"),
                Radio(value="SVM", label="Support Vector Machine (SVM)"),
                Divider(),
                Text("Deep Learning", weight="bold", size=14),
                Radio(value="ANN", label="Artificial Neural Network (ANN)"),
                Radio(value="LSTM", label="LSTM (Simulasi)"),
            ],
        ),
    )

    hasil = Text(size=16, weight="bold")

    # ================= AKSI =================
    def klasifikasi(e):
        try:
            nilai = float(input_penjualan.value)
            metode = radio_metode.value

            input_df = pd.DataFrame(
                [[nilai]],
                columns=["rata_penjualan"]
            )

            if metode == "Naive Bayes":
                pred = model_nb.predict(input_df)[0]

            elif metode == "KNN":
                pred = model_knn.predict(input_df)[0]

            elif metode == "SVM":
                pred = model_svm.predict(input_df)[0]

            elif metode == "ANN":
                pred = model_ann.predict(input_df)[0]

            elif metode == "LSTM":
                pred = lstm_predict(nilai)

            else:
                pred = "Tidak diketahui"

            hasil.value = f"📊 Hasil ({metode}): {pred}"
            hasil.color = Colors.GREEN

        except Exception as e:
            hasil.value = f"❌ Error: {e}"
            hasil.color = Colors.RED

        page.update()


    def reset(e):
        input_penjualan.value = ""
        hasil.value = ""
        page.update()

    # ================= UI =================
    page.add(
        Container(
            width=620,
            padding=30,
            bgcolor=Colors.WHITE,
            border_radius=24,
            shadow=BoxShadow(blur_radius=25, color=Colors.BLACK12),
            content=Column(
                spacing=20,
                controls=[
                    Text("Aplikasi Klasifikasi Penjualan", size=22, weight="bold"),

                    Row(
                        alignment="spaceBetween",
                        controls=[
                            Column(
                                spacing=10,
                                controls=[
                                    Text("Input Data", weight="bold"),
                                    input_penjualan,
                                ],
                            ),
                            Container(
                                width=280,
                                padding=15,
                                bgcolor=Colors.GREY_50,
                                border_radius=16,
                                content=radio_metode,
                            ),
                        ],
                    ),

                    Row(
                        alignment="center",
                        spacing=20,
                        controls=[
                            ElevatedButton(
                                "Klasifikasi",
                                icon=Icons.CHECK_CIRCLE,
                                on_click=klasifikasi,
                            ),
                            OutlinedButton(
                                "Reset",
                                icon=Icons.REFRESH,
                                on_click=reset,
                            ),
                        ],
                    ),

                    hasil,
                ],
            ),
        )
    )


app(main)
