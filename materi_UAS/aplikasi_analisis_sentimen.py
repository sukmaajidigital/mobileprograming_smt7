import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from flet import *
from textblob import TextBlob
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import torch

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression

# ================= TRANSFORMERS =================
from transformers import AutoTokenizer, AutoModelForSequenceClassification


def main(page: Page):
    # ================= KONFIGURASI PAGE =================
    page.title = "Analisis Sentimen"
    page.bgcolor = Colors.GREY_200
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    # ================= INIT NLTK =================
    nltk.download("vader_lexicon", quiet=True)
    vader = SentimentIntensityAnalyzer()

    # ================= INDO-BERT (STABIL & INDONESIA) =================
    indo_tokenizer = AutoTokenizer.from_pretrained(
        "mdhugol/indonesia-bert-sentiment-classification"
    )
    indo_model = AutoModelForSequenceClassification.from_pretrained(
        "mdhugol/indonesia-bert-sentiment-classification"
    )

    label_map_indo = {
        0: "Positif 😊",
        1: "Netral 😐",
        2: "Negatif 😞"
    }

    # ================= LOAD DATASET =================
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "data_sentimen_100.xlsx")

    if not os.path.exists(file_path):
        raise FileNotFoundError("❌ File data_sentimen_100.xlsx tidak ditemukan")

    df = pd.read_excel(file_path)
    data_teks = df["teks"].tolist()
    data_label = df["label"].tolist()

    # ================= TF-IDF =================
    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    X = vectorizer.fit_transform(data_teks)

    # ================= MODEL ML =================
    model_nb = MultinomialNB().fit(X, data_label)
    model_knn = KNeighborsClassifier(n_neighbors=5).fit(X.toarray(), data_label)
    model_ann = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=1000).fit(X, data_label)
    model_lr = LogisticRegression(max_iter=1000).fit(X, data_label)

    # ================= ANALISIS LEXICON =================
    def analisis_textblob(teks):
        p = TextBlob(teks).sentiment.polarity
        return "Positif 😊" if p > 0 else "Negatif 😞" if p < 0 else "Netral 😐"

    def analisis_vader(teks):
        c = vader.polarity_scores(teks)["compound"]
        return "Positif 😊" if c >= 0.05 else "Negatif 😞" if c <= -0.05 else "Netral 😐"

    # ================= ANALISIS ML =================
    def analisis_naive_bayes(teks):
        return model_nb.predict(vectorizer.transform([teks]))[0].capitalize()

    def analisis_knn(teks):
        return model_knn.predict(vectorizer.transform([teks]).toarray())[0].capitalize()

    def analisis_ann(teks):
        return model_ann.predict(vectorizer.transform([teks]))[0].capitalize()

    def analisis_lr(teks):
        return model_lr.predict(vectorizer.transform([teks]))[0].capitalize()

    # ================= ANALISIS TRANSFORMER =================
    def analisis_indobert(teks):
        inputs = indo_tokenizer(
            teks, return_tensors="pt", truncation=True, padding=True
        )
        with torch.no_grad():
            outputs = indo_model(**inputs)
            pred = torch.argmax(outputs.logits, dim=1).item()
        return label_map_indo[pred]

    # ================= AKSI BUTTON =================
    def analisis_sentimen(e):
        teks = input_ulasan.value.strip()
        metode = radio_metode.value

        if not teks:
            hasil.value = "❌ Teks ulasan tidak boleh kosong"
            hasil.color = Colors.RED
        else:
            fungsi = {
                "TextBlob": analisis_textblob,
                "VADER": analisis_vader,
                "Naive Bayes": analisis_naive_bayes,
                "KNN": analisis_knn,
                "ANN": analisis_ann,
                "Logistic Regression": analisis_lr,
                "IndoBERT": analisis_indobert,
            }

            prediksi = fungsi[metode](teks)
            hasil.value = f"📊 Hasil ({metode}): {prediksi}"
            hasil.color = Colors.GREEN

        page.update()

    def refresh_form(e):
        input_ulasan.value = ""
        radio_metode.value = "TextBlob"
        hasil.value = ""
        page.update()

    # ================= UI =================
    input_ulasan = TextField(
        label="Masukkan Ulasan",
        multiline=True,
        min_lines=4,
        max_lines=6,
        border_radius=12
    )

    radio_metode = RadioGroup(
        value="TextBlob",
        content=Column(
            spacing=5,
            controls=[

                # ===== LEXICON-BASED =====
                Text("Lexicon-Based Approach (Metode)", weight="bold", size=14),
                Radio(value="TextBlob", label="TextBlob"),
                Radio(value="VADER", label="VADER"),

                Divider(),

                # ===== MACHINE LEARNING =====
                Text("Machine Learning (Traditional, Algoritma)", weight="bold", size=14),
                Radio(value="Naive Bayes", label="Naive Bayes"),
                Radio(value="KNN", label="K-Nearest Neighbor (KNN)"),

                Divider(),

                # ===== DEEP LEARNING =====
                Text("Deep Learning (Algoritma)", weight="bold", size=14),
                Radio(value="ANN", label="Artificial Neural Network (ANN)"),
                Radio(value="Logistic Regression", label="CNN (Text CNN)"),

                Divider(),

                # ===== TRANSFORMER =====
                Text("Transformer-Based Models (Model)", weight="bold", size=14),
                Radio(value="IndoBERT", label="IndoBERT"),
            ]
        )
    )


    hasil = Text(size=14, weight="bold")

    page.add(
        Container(
            width=800,
            padding=30,
            bgcolor=Colors.WHITE,
            border_radius=24,
            shadow=BoxShadow(blur_radius=25, color=Colors.BLACK12),
            content=Column(
                horizontal_alignment="center",
                spacing=20,
                controls=[
                    Text("Analisis Sentimen", size=22, weight="bold"),
                    Row([
                        input_ulasan,
                        radio_metode,
                    ]),
                    ElevatedButton("Analisis Sentimen", on_click=analisis_sentimen),
                    OutlinedButton("Refresh Form", on_click=refresh_form),
                    hasil,
                ],
            ),
        )
    )


app(main)
