# 📊 Economic Resilience Intelligence (ERI)
**AI-Powered Decision Support System | Microsoft Elevate Datathon 2026**

![License](https://img.shields.io/github/license/RifqiBopp/Nama-Timnya-Apa)
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Framework](https://img.shields.io/badge/Framework-Flask%20%2F%20Streamlit-orange.svg)

## 🌟 Overview
**Economic Resilience Intelligence (ERI)** adalah platform analitik canggih yang dirancang untuk mengukur, memantau, dan memvisualisasikan ketahanan ekonomi daerah di Indonesia. Dengan memanfaatkan data transaksi digital (QRIS) dan indikator makroekonomi dari BPS, ERI memberikan wawasan mendalam bagi pembuat kebijakan untuk memperkuat stabilitas ekonomi regional.

Platform ini menggunakan algoritma **Machine Learning (K-Means Clustering)** untuk mengelompokkan provinsi berdasarkan profil resiliensi mereka: **Tangguh, Transisi, dan Rentan.**

## 🚀 Key Features
- **Interactive Dashboard:** Visualisasi peta tematik dan metrik KPI real-time (2025).
- **AI-Driven Clustering:** Pengelompokan daerah menggunakan K-Means untuk identifikasi kerentanan ekonomi.
- **Trend Analysis:** Pemantauan pertumbuhan PDRB dan volume QRIS secara quarterly (2024-2025).
- **Policy Recommendation:** Rekomendasi kebijakan otomatis berbasis AI untuk setiap kategori klaster.
- **Multi-Platform Support:** Tersedia dalam versi **Flask Dashboard** (Premium Custom UI) dan **Streamlit App** (Rapid Deployment).

## 🛠️ Tech Stack
- **Backend:** Python, Flask, Streamlit
- **Machine Learning:** Scikit-Learn (K-Means, MinMaxScaler), Joblib
- **Data Processing:** Pandas, Numpy
- **Visualization:** Plotly.js, D3.js (via Plotly)
- **Frontend:** Vanilla CSS (Azure AI Inspired Design), Material Symbols

## 📂 Project Structure
```text
├── data/
│   ├── processed/          # Data yang telah dibersihkan & diproses
├── models/
│   └── kmeans_model.pkl    # Model Machine Learning yang telah dilatih
├── static/                 # Assets (CSS, JS, Images)
├── templates/              # HTML Templates (Flask)
├── app.py                  # Streamlit Main Application
├── server.py               # Flask Main Application
└── requirements.txt        # Python Dependencies
```

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RifqiBopp/Nama-Timnya-Apa.git
   cd Nama-Timnya-Apa
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   - **Flask Version (Dashboard):**
     ```bash
     python server.py
     ```
   - **Streamlit Version:**
     ```bash
     streamlit run app.py
     ```

## 🧠 Methodology
Indeks Ketahanan Ekonomi dihitung menggunakan bobot komposit dari:
1. **PDRB (35%)**: Kapasitas output ekonomi.
2. **Volume QRIS (35%)**: Tingkat adopsi ekonomi digital.
3. **Tingkat Kemiskinan (30%)**: Indikator kerentanan sosial (Inverse weight).

Model Clustering kemudian membagi wilayah menjadi 3 kategori untuk memberikan rekomendasi kebijakan yang preskriptif dan tepat sasaran.

---
**Developed for Microsoft Elevate Datathon 2026**
*Contact: [apriansyahrifqii@gmail.com](mailto:apriansyahrifqii@gmail.com)*