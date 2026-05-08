import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import joblib
import os
import json

def load_and_clean_data(raw_data_path):
    """Memuat data mentah dan membersihkannya."""
    df = pd.read_csv(raw_data_path)
    # Pembersihan missing values
    df.fillna(df.median(numeric_only=True), inplace=True)
    return df

def feature_engineering(df):
    """Melakukan rekayasa fitur untuk menghitung Resilience Index."""
    
    # --- 1. Normalisasi tiap komponen ke 0-1 ---
    scaler_mm = MinMaxScaler()
    
    # PDRB (semakin tinggi semakin baik)
    df['PDRB_Norm'] = scaler_mm.fit_transform(df[['PDRB_Triliun']])
    
    # Volume QRIS (semakin tinggi semakin baik)
    df['QRIS_Norm'] = scaler_mm.fit_transform(df[['Volume_QRIS_Juta']])
    
    # Kemiskinan (semakin rendah semakin baik → inverse)
    df['Poverty_Inv_Norm'] = 1 - scaler_mm.fit_transform(df[['Tingkat_Kemiskinan_Persen']])
    
    # --- 2. Weighted Composite Score ---
    # Bobot: PDRB 35%, QRIS Adoption 35%, Inverse Poverty 30%
    df['Raw_Resilience'] = (
        df['PDRB_Norm'] * 0.35 +
        df['QRIS_Norm'] * 0.35 +
        df['Poverty_Inv_Norm'] * 0.30
    )
    
    # --- 3. Skala 1-10 ---
    min_val = df['Raw_Resilience'].min()
    max_val = df['Raw_Resilience'].max()
    df['Economic_Resilience_Index'] = np.interp(
        df['Raw_Resilience'], (min_val, max_val), (1.0, 10.0)
    )
    df['Economic_Resilience_Index'] = np.round(df['Economic_Resilience_Index'], 2)
    
    # --- 4. Digital Adoption Score (0-100) ---
    df['Digital_Adoption_Score'] = np.round(df['QRIS_Norm'] * 100, 1)
    
    # Hapus kolom intermediary
    df.drop(columns=['PDRB_Norm', 'QRIS_Norm', 'Poverty_Inv_Norm', 'Raw_Resilience'], inplace=True)
    
    return df

def train_model(df, features, model_save_path):
    """Melatih model K-Means clustering."""
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[features])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(scaled_features)
    
    # --- Relabel clusters berdasarkan rata-rata resilience ---
    cluster_means = df.groupby('Cluster')['Economic_Resilience_Index'].mean()
    sorted_clusters = cluster_means.sort_values().index.tolist()
    
    # Map: lowest mean → 1 (Rentan), mid → 0 (Transisi), highest → 2 (Tangguh)
    remap = {sorted_clusters[0]: 1, sorted_clusters[1]: 0, sorted_clusters[2]: 2}
    df['Cluster'] = df['Cluster'].map(remap)

    # Menyimpan model
    model_data = {
        'kmeans': kmeans,
        'scaler': scaler,
        'cluster_remap': remap
    }
    os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
    joblib.dump(model_data, model_save_path)
    return df

def generate_trend_data(df, output_path):
    """Generate data trend quarterly sintetis untuk Trend Analysis."""
    quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025']
    
    trend_records = []
    np.random.seed(42)
    
    for _, row in df.iterrows():
        base_qris = row['Volume_QRIS_Juta']
        base_pdrb = row['PDRB_Triliun']
        
        for i, q in enumerate(quarters):
            # Simulasi pertumbuhan QRIS (growth 3-8% per quarter)
            growth_factor = 1 + (0.03 + np.random.uniform(0, 0.05)) * i
            noise = np.random.uniform(-0.02, 0.02)
            qris_val = round(base_qris * (growth_factor + noise) / (1 + 0.03 * len(quarters)), 2)
            
            # PDRB grows slower (1-2% per quarter)
            pdrb_growth = 1 + (0.01 + np.random.uniform(0, 0.01)) * i
            pdrb_val = round(base_pdrb * pdrb_growth / (1 + 0.01 * len(quarters)), 2)
            
            trend_records.append({
                'Provinsi': row['Provinsi'],
                'Quarter': q,
                'Volume_QRIS_Juta': max(0.5, qris_val),
                'PDRB_Triliun': max(10, pdrb_val)
            })
    
    trend_df = pd.DataFrame(trend_records)
    trend_df.to_csv(output_path, index=False)
    return trend_df

if __name__ == '__main__':
    print("=" * 50)
    print("  Economic Resilience Data Pipeline")
    print("=" * 50)
    
    print("\n[1/4] Memuat dan membersihkan data BPS...")
    raw_df = load_and_clean_data('../data/raw/bps_economic_data_2025.csv')
    print(f"      -> {len(raw_df)} provinsi dimuat")
    
    print("[2/4] Feature engineering & Resilience Index...")
    processed_df = feature_engineering(raw_df)
    print(f"      -> Index range: {processed_df['Economic_Resilience_Index'].min()} - {processed_df['Economic_Resilience_Index'].max()}")
    
    print("[3/4] Training K-Means clustering model...")
    final_df = train_model(processed_df, ['PDRB_Triliun', 'Volume_QRIS_Juta'], '../models/kmeans_economic_model.pkl')
    
    cluster_map = {0: 'Transisi', 1: 'Rentan', 2: 'Tangguh'}
    final_df['Status'] = final_df['Cluster'].map(cluster_map)
    print(f"      -> Cluster distribution:\n{final_df['Status'].value_counts().to_string()}")
    
    final_df.to_csv('../data/processed/clean_data.csv', index=False)
    
    print("[4/4] Generating trend data (quarterly)...")
    trend_df = generate_trend_data(final_df, '../data/processed/trend_data.csv')
    print(f"      -> {len(trend_df)} trend records generated")
    
    print("\n[OK] Pipeline selesai. Semua data dan model telah disimpan.")
