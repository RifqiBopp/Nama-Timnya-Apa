import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib

# --- CONFIG UI ---
st.set_page_config(page_title="Economic Resilience Intelligence", page_icon="📈", layout="wide")

# --- 1. DATA LOADER ---
@st.cache_data
def load_data():
    # Memuat data asli/representatif dari BPS dan BI (QRIS)
    df = pd.read_csv('data/processed/clean_data.csv')
    return df

df = load_data()

# --- 2. MACHINE LEARNING: K-MEANS CLUSTERING ---
@st.cache_resource
def load_model():
    return joblib.load('models/kmeans_economic_model.pkl')

model_data = load_model()
kmeans = model_data['kmeans']
scaler = model_data['scaler']

# Terapkan scaler dan prediksi dari model yang disimpan
features = ['PDRB_Triliun', 'Volume_QRIS_Juta']
scaled_features = scaler.transform(df[features])
df['Cluster'] = kmeans.predict(scaled_features)

# Mapping nama cluster agar lebih mudah dipahami UI
# Disesuaikan agar logis berdasarkan sentroid model
cluster_map = {
    0: 'Transisi (Moderate)', 
    1: 'Berkembang (Vulnerable)', 
    2: 'Tangguh (High Resilience)'
}
df['Status'] = df['Cluster'].map(cluster_map)

# --- 3. UI / UX DASHBOARD ---
st.title("📊 Regional Economic Resilience Intelligence")
st.markdown("**AI-Powered Decision Support System | Microsoft Elevate Datathon 2026**")
st.divider()

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Provinsi Dianalisis", len(df))
col2.metric("Rata-rata Resilience Index", f"{df['Economic_Resilience_Index'].mean():.2f}/10")
col3.metric("Total Transaksi QRIS", f"{df['Volume_QRIS_Juta'].sum():.0f} Juta")
col4.metric("Provinsi Paling Tangguh", df.loc[df['Economic_Resilience_Index'].idxmax()]['Provinsi'])

st.divider()

# Visualisasi Grafik Interaktif
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Clustering: PDRB vs Transaksi QRIS")
    # Scatter plot dengan ukuran bubble = Resilience Index
    fig_scatter = px.scatter(
        df, x='Volume_QRIS_Juta', y='PDRB_Triliun', 
        size='Economic_Resilience_Index', color='Status',
        hover_name='Provinsi', size_max=40,
        labels={'Volume_QRIS_Juta': 'Volume QRIS (Juta Transaksi)', 'PDRB_Triliun': 'PDRB (Triliun Rp)'}
    )
    fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_chart2:
    st.subheader("Economic Resilience Index Ranking")
    # Ambil 15 besar agar UI tidak terlalu penuh
    top_df = df.sort_values('Economic_Resilience_Index', ascending=False).head(15)
    fig_bar = px.bar(
        top_df.sort_values('Economic_Resilience_Index', ascending=True), 
        x='Economic_Resilience_Index', y='Provinsi', 
        orientation='h', color='Economic_Resilience_Index',
        color_continuous_scale='Blues'
    )
    fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bar, use_container_width=True)

# Bagian AI Policy Recommendation
st.subheader("🧠 AI-Driven Policy Recommendations")
selected_region = st.selectbox("Pilih Provinsi untuk melihat rekomendasi kebijakan:", df['Provinsi'])
region_data = df[df['Provinsi'] == selected_region].iloc[0]

with st.expander(f"Tampilkan Rekomendasi Strategis untuk {selected_region}", expanded=True):
    st.write(f"**Kategori Klaster:** `{region_data['Status']}`")
    st.write(f"**Skor Resiliensi:** `{region_data['Economic_Resilience_Index']:.2f} / 10`")
    
    # Logika preskriptif berdasarkan klaster K-Means (Disesuaikan Map nya)
    status = region_data['Status']
    if status == 'Berkembang (Vulnerable)':
        st.error("🚨 **Rekomendasi Kebijakan:** Tingkat adopsi digital rendah dan rentan guncangan ekonomi. Fokuskan APBD untuk subsidi internet UMKM dan pelatihan literasi pembayaran digital dasar.")
    elif status == 'Tangguh (High Resilience)':
        st.success("✅ **Rekomendasi Kebijakan:** Ekonomi sangat tangguh dengan digitalisasi tinggi. Pemda dapat beralih ke program pendanaan *scale-up* UMKM menuju ekspor dan penguatan regulasi keamanan siber.")
    else:
        st.warning("⚠️ **Rekomendasi Kebijakan:** Daerah dalam masa transisi. Tingkatkan kampanye penggunaan QRIS di pasar tradisional dan perluas kerja sama BPD (Bank Pembangunan Daerah) dengan Fintech.")

st.divider()
st.subheader("Raw Data Preview")
st.dataframe(df, use_container_width=True)
