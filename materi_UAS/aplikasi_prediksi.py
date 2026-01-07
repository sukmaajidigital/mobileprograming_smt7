from flet import *
import numpy as np
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor

import warnings
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings("ignore", category=ConvergenceWarning)


def main(page: Page):
    page.title = "Prediksi Penjualan"
    page.bgcolor = Colors.GREY_100
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # ================= INPUT =================
    input_penjualan = [
        TextField(
            label=f"Periode {i+1}",
            keyboard_type=KeyboardType.NUMBER,
            width=180,
            border_radius=10,
        )
        for i in range(10)
    ]

    kolom_kiri = Column(controls=input_penjualan[:5], spacing=10)
    kolom_kanan = Column(controls=input_penjualan[5:], spacing=10)

    # ================= METODE =================
    def moving_average(data):
        return sum(data[-3:]) / 3

    def exponential_smoothing(data, alpha=0.3):
        hasil = data[0]
        for val in data[1:]:
            hasil = alpha * val + (1 - alpha) * hasil
        return hasil

    def knn_predict(data):
        X = np.arange(len(data)).reshape(-1, 1)
        y = np.array(data)
        return KNeighborsRegressor(3).fit(X, y).predict([[len(data)]])[0]

    def decision_tree_predict(data):
        X = np.arange(len(data)).reshape(-1, 1)
        y = np.array(data)
        return DecisionTreeRegressor().fit(X, y).predict([[len(data)]])[0]

    def ann_predict(data):
        X = np.arange(len(data)).reshape(-1, 1)
        y = np.array(data)
        return MLPRegressor(max_iter=2000).fit(X, y).predict([[len(data)]])[0]

    def lstm_predict(data):
        return sum(data[-3:]) / 3  # simulasi

    # ================= RADIO =================
    radio = RadioGroup(
        value="Moving Average",
        content=Column(
            controls=[
                Text("Metode Statistik", weight="bold", size=14),
                Radio(value="Moving Average", label="Moving Average"),
                Radio(value="Exponential Smoothing", label="Exponential Smoothing"),
                Divider(),
                Text("Algoritma Machine Learning (Traditional)", weight="bold", size=14),
                Radio(value="KNN", label="K-Nearest Neighbor"),
                Radio(value="Decision Tree", label="Decision Tree"),
                Divider(),
                Text("Algoritma Deep Learning", weight="bold", size=14),
                Radio(value="ANN", label="Artificial Neural Network"),
                Radio(value="LSTM", label="LSTM"),
            ]
        ),
    )

    hasil = Text(weight="bold", size=16)

    # ================= AKSI =================
    def prediksi(e):
        try:
            data = [float(tf.value) for tf in input_penjualan if tf.value]

            if len(data) < 3:
                hasil.value = "❌ Minimal 3 data penjualan"
                hasil.color = Colors.RED
            else:
                metode = radio.value
                pred = {
                    "Moving Average": moving_average,
                    "Exponential Smoothing": exponential_smoothing,
                    "KNN": knn_predict,
                    "Decision Tree": decision_tree_predict,
                    "ANN": ann_predict,
                    "LSTM": lstm_predict,
                }[metode](data)

                hasil.value = f"📈 Prediksi ({metode}): {pred:.2f}"
                hasil.color = Colors.GREEN

        except:
            hasil.value = "❌ Semua input harus angka"
            hasil.color = Colors.RED

        page.update()

    def reset(e):
        for tf in input_penjualan:
            tf.value = ""
        hasil.value = ""
        page.update()

    # ================= UI =================
    page.add(
        Container(
            width=900,
            padding=30,
            bgcolor=Colors.WHITE,
            border_radius=24,
            shadow=BoxShadow(blur_radius=30, color=Colors.BLACK12),
            content=Column(
                spacing=25,
                controls=[
                    Text("Prediksi Penjualan", size=24, weight="bold"),
                    Text("Masukkan data penjualan 10 periode"),

                    Row(
                        alignment="spaceBetween",
                        controls=[
                            Column(
                                spacing=15,
                                controls=[
                                    Text("Data Penjualan", weight="bold"),
                                    Row(
                                        spacing=20,
                                        controls=[kolom_kiri, kolom_kanan],
                                    ),
                                ],
                            ),

                            Container(
                                width=260,
                                padding=20,
                                bgcolor=Colors.GREY_50,
                                border_radius=16,
                                content=Column(
                                    spacing=10,
                                    controls=[
                                        Text("Silahkan pilih : ", weight="bold"),
                                        radio,
                                    ],
                                ),
                            ),
                        ],
                    ),

                    Row(
                        alignment="center",
                        spacing=20,
                        controls=[
                            ElevatedButton(
                                "Prediksi",
                                icon=Icons.SHOW_CHART,
                                on_click=prediksi,
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
