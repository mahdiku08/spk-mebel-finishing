import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.metrics import silhouette_score
import streamlit as st
from tslearn.clustering import TimeSeriesKMeans
from tslearn.metrics import cdist_dtw
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

# ==========================================================
# 1. FUNGSI EVALUASI SILHOUETTE SCORE (DTW)
# ==========================================================


def calculate_dtw_silhouette(data_norm, cluster_labels):
  """Menghitung Silhouette Score menggunakan Precomputed DTW Distance Matrix."""
  unique_clusters = np.unique(cluster_labels)
  if len(unique_clusters) < 2 or len(unique_clusters) >= len(data_norm):
    return 0.0

  dist_matrix = cdist_dtw(data_norm)
  score = silhouette_score(
      dist_matrix, cluster_labels, metric="precomputed", random_state=42
  )
  return float(score)


# ==========================================================
# 2. DETEKSI LONJAKAN PERMINTAAN (SPIKE DETECTION)
# ==========================================================


def detect_demand_spikes(df, threshold_percentage=30):
  """Mendeteksi bulan yang mengalami lonjakan penjualan total >= threshold_percentage (%)."""
  angka = df.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").fillna(0)
  total_bulanan = angka.sum()

  spikes = []
  cols = list(total_bulanan.index)
  for i in range(1, len(cols)):
    prev_val = total_bulanan.iloc[i - 1]
    curr_val = total_bulanan.iloc[i]
    if prev_val > 0:
      pct_change = ((curr_val - prev_val) / prev_val) * 100
      if pct_change >= threshold_percentage:
        spikes.append({
            "bulan": cols[i],
            "bulan_sebelumnya": cols[i - 1],
            "kenaikan_unit": curr_val - prev_val,
            "persentase": pct_change,
            "total_unit": curr_val,
        })
  return spikes, total_bulanan


# ==========================================================
# 3. PIPELINE PREPROCESSING & CLUSTERING TIME SERIES
# ==========================================================


def run_clustering_pipeline(df):
  """Menjalankan preprocessing data, TimeSeriesKMeans DTW, penyusunan urutan klaster, dan Silhouette."""
  kolom_produk = df.columns[0]

  # 1. Membersihkan baris summary/total
  df_clean = df[
      ~df[kolom_produk]
      .astype(str)
      .str.lower()
      .str.contains("total|jumlah|grand total|rata")
  ].reset_index(drop=True)

  # 2. Parsing kolom numerik periode
  angka = df_clean.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").fillna(0)
  df_clean.iloc[:, 1:] = angka
  nama_produk = df_clean.iloc[:, 0].astype(str).tolist()
  data = angka.values

  if len(nama_produk) < 3:
    return (
        None,
        "Minimal diperlukan 3 varian produk untuk menjalankan clustering (K ="
        " 3).",
    )

  # 3. Reshape Time-Series & Z-Score Normalization
  data_ts = data.reshape(data.shape[0], data.shape[1], 1)
  scaler = TimeSeriesScalerMeanVariance()
  data_norm = scaler.fit_transform(data_ts)

  # 4. Pemodelan TimeSeriesKMeans dengan batas Sakoe-Chiba
  model = TimeSeriesKMeans(
      n_clusters=3,
      metric="dtw",
      metric_params={
          "global_constraint": "sakoe_chiba",
          "sakoe_chiba_radius": 2,
      },
      max_iter_barycenter=10,
      n_init=5,
      random_state=42,
      max_iter=50,
  )
  raw_cluster = model.fit_predict(data_norm)

  # 5. Pengurutan & Remapping Klaster Berdasarkan Total Volume Penjualan
  total_per_produk = angka.sum(axis=1)
  mean_per_cluster = {}
  for c_id in range(3):
    mean_per_cluster[c_id] = total_per_produk[raw_cluster == c_id].mean()

  sorted_by_val = sorted(
      mean_per_cluster, key=mean_per_cluster.get, reverse=True
  )
  cluster_map = {
      sorted_by_val[1]: 0,  # Klaster 0: Sedang / Safety Stock
      sorted_by_val[0]: 1,  # Klaster 1: Stabil & Stok Ada / MTS
      sorted_by_val[2]: 2,  # Klaster 2: Rendah / MTO
  }
  cluster = np.array([cluster_map[c] for c in raw_cluster])

  # 6. Hitung Silhouette Score DTW
  silhouette_val = calculate_dtw_silhouette(data_norm, cluster)

  return {
      "dataset": df_clean,
      "produk": nama_produk,
      "data_norm": data_norm,
      "cluster": cluster,
      "model": model,
      "silhouette": silhouette_val,
  }, None


# ==========================================================
# 4. DASHBOARD PAGE VIEW
# ==========================================================


def dashboard_page():
  default_keys = [
      "dataset",
      "produk",
      "data_norm",
      "cluster",
      "model",
      "silhouette",
      "rekomendasi",
  ]
  for key in default_keys:
    if key not in st.session_state:
      st.session_state[key] = None

  st.markdown(
      """
        <div style="margin-bottom: 24px;">
            <h2 style="color: #0F172A; font-weight: 800; margin-bottom: 6px;">Dashboard Overview</h2>
            <p style="color: #64748B; font-size: 0.95rem; margin: 0;">
                Sistem Pendukung Keputusan Perencanaan Produksi Finishing Mebel menggunakan Time Series Clustering dan Dynamic Time Warping
            </p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  # Section Unggah File
  if st.session_state.dataset is None:
    st.markdown(
        """
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <h4 style="color: #1E293B; font-size: 1.05rem; font-weight: 700; margin-top: 0; margin-bottom: 12px;">📁 Upload Dataset Transaksi Penjualan</h4>
            </div>
            """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload file Excel (.xlsx)",
        type=["xlsx"],
        help=(
            "Unggah berkas Excel transaksi penjualan untuk diproses oleh sistem"
        ),
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
      try:
        with st.spinner("Dataset sedang diproses..."):
          df_raw = pd.read_excel(uploaded_file)

          if df_raw.shape[1] < 3:
            st.error(
                "Dataset minimal terdiri dari 1 kolom nama varian mebel dan"
                " minimal 2 kolom periode penjualan."
            )
            return

          results, err_msg = run_clustering_pipeline(df_raw)

          if err_msg:
            st.error(err_msg)
            return

          for key, value in results.items():
            st.session_state[key] = value

          st.rerun()

      except Exception as e:
        st.error(f"Gagal membaca atau memproses berkas Excel: {e}")
        return

  else:
    col_msg, col_reset = st.columns([4, 1])
    with col_msg:
      st.success(
          "✅ Dataset transaksi berhasil diunggah dan disimpan ke dalam memori"
          " sistem."
      )
    with col_reset:
      if st.button("🔄 Ganti Dataset", use_container_width=True):
        for key in default_keys:
          st.session_state[key] = None
        st.rerun()

  # Konten Utama Dashboard
  if st.session_state.dataset is not None:
    df = st.session_state.dataset
    jumlah_produk = len(df)
    jumlah_periode = df.shape[1] - 1

    # Metric Cards
    m1, m2, m3 = st.columns(3)
    with m1:
      st.markdown(
          f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <p style="color: #64748B; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px;">Total Varian Produk</p>
                <div style="display: flex; align-items: baseline; gap: 8px;">
                    <span style="color: #0F172A; font-size: 2.2rem; font-weight: 800;">{jumlah_produk}</span>
                    <span style="color: #0284C7; font-size: 0.9rem; font-weight: 700;">Varian Mebel</span>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with m2:
      st.markdown(
          f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <p style="color: #64748B; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px;">Periode Transaksi</p>
                <div style="display: flex; align-items: baseline; gap: 8px;">
                    <span style="color: #0F172A; font-size: 2.2rem; font-weight: 800;">{jumlah_periode}</span>
                    <span style="color: #0284C7; font-size: 0.9rem; font-weight: 700;">Bulan</span>
                </div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with m3:
      st.markdown(
          """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <p style="color: #64748B; font-size: 0.85rem; font-weight: 600; margin-bottom: 12px;">Status Pipeline</p>
                <span style="background-color: #DCFCE7; color: #166534; padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; display: inline-block;">Analisis Siap</span>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown("<br>", unsafe_allow_html=True)

    # Spike Detection
    spikes, total_bulanan = detect_demand_spikes(df, threshold_percentage=30)
    if spikes:
      top_spike = max(spikes, key=lambda x: x["persentase"])
      st.markdown(
          f"""
            <div style="background-color: #FEF3C7; border: 1px solid #F59E0B; border-left: 6px solid #D97706; border-radius: 10px; padding: 16px 20px; margin-bottom: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span style="font-size: 1.2rem;">⚡</span>
                    <h4 style="color: #92400E; font-size: 1rem; font-weight: 800; margin: 0;">PEMBERITAHUAN: LONJAKAN PERMINTAAN TERDETEKSI!</h4>
                </div>
                <p style="color: #78350F; font-size: 0.88rem; margin: 0; line-height: 1.5;">
                    Terdeteksi lonjakan permintaan signifikan pada bulan <b>{top_spike['bulan']}</b> sebesar 
                    <b style="color: #D97706;">+{top_spike['persentase']:.1f}%</b> 
                    (kenaikan <b>{int(top_spike['kenaikan_unit']):,} unit</b> dari bulan {top_spike['bulan_sebelumnya']}). 
                    Total transaksi mencapai <b>{int(top_spike['total_unit']):,} unit</b>.
                </p>
            </div>
            """,
          unsafe_allow_html=True,
      )

    # Trend Chart
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px 12px 0 0; padding: 16px 20px; border-bottom: none;">
            <h4 style="color: #1E293B; font-size: 1rem; font-weight: 700; margin: 0;">📈 Trend Penjualan Bulanan (Seluruh Varian)</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = px.line(
        x=df.columns[1:],
        y=total_bulanan.values,
        markers=True,
        template="plotly_white",
    )
    fig.update_traces(
        line=dict(color="#0284C7", width=3.5),
        marker=dict(size=8, color="#0284C7", symbol="circle"),
    )

    if spikes:
      spike_months = [s["bulan"] for s in spikes]
      spike_values = [total_bulanan[m] for m in spike_months]
      fig.add_scatter(
          x=spike_months,
          y=spike_values,
          mode="markers+text",
          marker=dict(color="#D97706", size=13, symbol="triangle-up"),
          text=["⚡ Lonjakan" for _ in spike_months],
          textposition="top center",
          name="Lonjakan Permintaan",
      )

    fig.update_layout(
        height=380,
        xaxis_title="Bulan Transaksi",
        yaxis_title="Volume Penjualan (Unit)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px 12px 0 0; padding: 16px 20px; border-bottom: none;">
            <h4 style="color: #1E293B; font-size: 1rem; font-weight: 700; margin: 0;">📋 Preview Data Transaksi Mebel</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(df, use_container_width=True, hide_index=True)