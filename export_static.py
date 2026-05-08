import pandas as pd
import numpy as np
import joblib
import json
import os

def export_data():
    # 1. Load Data
    df = pd.read_csv('data/processed/clean_data.csv')
    trend_df = pd.read_csv('data/processed/trend_data.csv')
    
    # 2. Load Model & Predict
    model_data = joblib.load('models/kmeans_economic_model.pkl')
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
        
    cluster_map = {0: 'Transisi', 1: 'Rentan', 2: 'Tangguh'}
    df['Status'] = df['Cluster'].map(cluster_map).fillna('Transisi')
    
    # 3. Calculate Stats
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
    
    # 4. Generate Recommendations for each province
    provinces_data = df.to_dict('records')
    for p in provinces_data:
        cluster = p.get('Cluster', 0)
        if cluster == 1:
            p['recommendation'] = {
                'level': 'critical',
                'title': 'Prioritas Tinggi - Rentan',
                'text': 'Tingkat adopsi digital rendah dan rentan guncangan ekonomi. Fokuskan APBD untuk subsidi internet UMKM, pelatihan literasi pembayaran digital dasar, dan insentif merchant QRIS di pasar tradisional.',
                'actions': [
                    'Subsidi koneksi internet untuk UMKM di daerah terpencil',
                    'Program pelatihan literasi digital dan keuangan massal',
                    'Kerja sama dengan BPD untuk edukasi QRIS',
                    'Insentif pajak untuk merchant yang mengadopsi pembayaran digital'
                ]
            }
        elif cluster == 2:
            p['recommendation'] = {
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
            p['recommendation'] = {
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
        
        # Add trend for this province
        p['trend'] = trend_df[trend_df['Provinsi'] == p['Provinsi']].to_dict('records')

    # 5. Save to JSON
    output = {
        "stats": stats,
        "provinces_data": provinces_data,
        "trend_data": trend_df.to_dict('records')
    }
    
    with open('data/static_data.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print("Success: data/static_data.json generated!")

if __name__ == "__main__":
    export_data()
