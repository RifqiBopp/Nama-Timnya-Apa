from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import json

app = Flask(__name__)

# --- DATA LOADER ---
def load_data():
    df = pd.read_csv('data/processed/clean_data.csv')
    df['Volume_QRIS_Juta'] = pd.to_numeric(df['Volume_QRIS_Juta'], errors='coerce')
    df['PDRB_Triliun'] = pd.to_numeric(df['PDRB_Triliun'], errors='coerce')
    return df

def load_trend_data():
    path = 'data/processed/trend_data.csv'
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def load_model():
    model_path = 'models/kmeans_economic_model.pkl'
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

# --- INIT ---
df = load_data()
trend_df = load_trend_data()
model_data = load_model()

if model_data:
    kmeans = model_data['kmeans']
    scaler = model_data['scaler']
    remap = model_data.get('cluster_remap', {})
    features = ['PDRB_Triliun', 'Volume_QRIS_Juta']
    scaled_features = scaler.transform(df[features])
    raw_clusters = kmeans.predict(scaled_features)
    if remap:
        df['Cluster'] = pd.Series(raw_clusters).map(remap).values
    else:
        df['Cluster'] = raw_clusters
else:
    df['Cluster'] = 0

cluster_map = {0: 'Transisi', 1: 'Rentan', 2: 'Tangguh'}
df['Status'] = df['Cluster'].map(cluster_map).fillna('Transisi')

# Ensure Digital_Adoption_Score exists
if 'Digital_Adoption_Score' not in df.columns:
    from sklearn.preprocessing import MinMaxScaler
    mm = MinMaxScaler()
    df['Digital_Adoption_Score'] = np.round(mm.fit_transform(df[['Volume_QRIS_Juta']]) * 100, 1).flatten()

print(f"[SERVER] Data loaded: {len(df)} provinces, {len(trend_df)} trend records")
print(f"[SERVER] Cluster distribution:\n{df['Status'].value_counts().to_string()}")

# --- ROUTES ---

@app.route('/')
def index():
    # Stats
    stats = {
        "total_provinces": int(len(df)),
        "avg_resilience": round(float(df['Economic_Resilience_Index'].mean()), 2),
        "total_qris": round(float(df['Volume_QRIS_Juta'].sum()), 0),
        "top_resilient": str(df.loc[df['Economic_Resilience_Index'].idxmax()]['Provinsi']),
        "top_resilient_score": round(float(df['Economic_Resilience_Index'].max()), 2),
        "avg_digital_adoption": round(float(df['Digital_Adoption_Score'].mean()), 1),
        "cluster_counts": {
            "tangguh": int((df['Status'] == 'Tangguh').sum()),
            "transisi": int((df['Status'] == 'Transisi').sum()),
            "rentan": int((df['Status'] == 'Rentan').sum()),
        }
    }

    # All province data for charts
    provinces_data = df.to_dict('records')
    
    # Trend data
    trend_data = trend_df.to_dict('records') if not trend_df.empty else []

    return render_template('index.html',
        stats=stats,
        provinces_data=json.dumps(provinces_data, default=str),
        trend_data=json.dumps(trend_data, default=str)
    )

@app.route('/api/data')
def get_data():
    return jsonify(df.to_dict('records'))

@app.route('/api/province/<name>')
def get_province(name):
    province = df[df['Provinsi'] == name]
    if province.empty:
        return jsonify({"error": "Province not found"}), 404
    
    data = province.iloc[0].to_dict()
    
    # Get trend for this province
    if not trend_df.empty:
        prov_trend = trend_df[trend_df['Provinsi'] == name].to_dict('records')
        data['trend'] = prov_trend
    
    # AI Recommendation
    cluster = data.get('Cluster', 0)
    if cluster == 1:
        data['recommendation'] = {
            'level': 'critical',
            'title': 'Prioritas Tinggi - Rentan',
            'text': 'Tingkat adopsi digital rendah dan rentan guncangan ekonomi. Fokuskan APBD untuk subsidi internet UMKM, pelatihan literasi pembayaran digital dasar, dan insentif merchant QRIS di pasar tradisional.',
            'actions': [
                'Subsidi koneksi internet untuk UMKM di daerah terpencil',
                'Program pelatihan literasi digital dan keuangan massal',
                'Kerja sama dengan Bank Pembangunan Daerah untuk edukasi QRIS',
                'Insentif pajak untuk merchant yang mengadopsi pembayaran digital'
            ]
        }
    elif cluster == 2:
        data['recommendation'] = {
            'level': 'optimal',
            'title': 'Optimal - Tangguh',
            'text': 'Ekonomi sangat tangguh dengan digitalisasi tinggi. Pemda dapat beralih ke program pendanaan scale-up UMKM menuju ekspor dan penguatan regulasi keamanan siber.',
            'actions': [
                'Program scale-up UMKM digital menuju pasar ekspor',
                'Penguatan infrastruktur keamanan siber daerah',
                'Pengembangan ekosistem fintech dan startup digital',
                'Menjadi model percontohan untuk daerah lain'
            ]
        }
    else:
        data['recommendation'] = {
            'level': 'transition',
            'title': 'Masa Transisi - Moderat',
            'text': 'Daerah dalam masa transisi menuju digitalisasi penuh. Tingkatkan kampanye penggunaan QRIS di pasar tradisional dan perluas kerja sama BPD dengan Fintech.',
            'actions': [
                'Kampanye penggunaan QRIS di pasar tradisional dan warung',
                'Kerja sama BPD dengan platform fintech untuk inklusi keuangan',
                'Peningkatan infrastruktur jaringan internet di daerah pelosok',
                'Pilot project smart village berbasis pembayaran digital'
            ]
        }
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
