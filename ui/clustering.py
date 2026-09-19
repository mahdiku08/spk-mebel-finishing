import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def clustering_page():

  # 1. HEADER HALAMAN
  st.markdown(
      """
    <div translate="no" class="notranslate">
        <h2 style="color: #0F172A; font-weight: 800; margin-bottom: 6px;">Hasil Time Series Clustering</h2>
        <p style="color: #64748B; font-size: 0.95rem; margin: 0 0 20px 0;">
            Pengelompokan varian finishing berdasarkan karakteristik fluktuasi histori penjualan (DTW)
        </p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 2. VALIDASI DATASET
  if (
      st.session_state.get("cluster") is None
      or st.session_state.get("dataset") is None
      or st.session_state.get("data_norm") is None
  ):
    st.warning(
        "⚠️ Belum ada data hasil clustering. Silakan unggah dataset pada menu"
        " **Dashboard** terlebih dahulu."
    )
    return

  df = st.session_state.dataset
  cluster = st.session_state.cluster
  data_norm = st.session_state.data_norm
  silhouette = st.session_state.get("silhouette", 0.0)
  period_cols = df.columns[1:]

  # Hitung Centroid Riil per Klaster
  centroids = {}
  for c_id in [0, 1, 2]:
    members = data_norm[cluster == c_id]
    if len(members) > 0:
      centroids[c_id] = members.mean(axis=0).ravel()
    else:
      centroids[c_id] = np.zeros(len(period_cols))

  # Hitung Jumlah Anggota tiap Klaster
  c0_count = int(np.sum(cluster == 0))
  c1_count = int(np.sum(cluster == 1))
  c2_count = int(np.sum(cluster == 2))

  # 3. STATUS VALIDASI SISTEM & SILHOUETTE SCORE
  st.markdown(
      f"""
    <div translate="no" class="notranslate" style="background-color: #1E293B; border-radius: 12px; padding: 18px 24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.12); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        <div>
            <p style="color: #94A3B8; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px;">STATUS SPK FINISHING MEBEL</p>
            <div style="display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap;">
                <span style="color: #38BDF8; font-size: 1.45rem; font-weight: 800;">3 Klaster Produksi Terbentuk</span>
                <span style="color: #CBD5E1; font-size: 0.88rem;">(Time Series K-Means DTW: MTS, Safety Stock, MTO)</span>
            </div>
        </div>
        <div style="background-color: #0F172A; border: 1px solid #334155; border-radius: 10px; padding: 8px 18px; text-align: right;">
            <p style="color: #94A3B8; font-size: 0.72rem; font-weight: 700; margin: 0; text-transform: uppercase; letter-spacing: 0.05em;">Evaluasi Validasi</p>
            <span style="color: #38BDF8; font-size: 1.25rem; font-weight: 800;">Silhouette Score: {silhouette:.4f}</span>
        </div>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # 4. KARTU KLASTER STRATEGI OPERASIONAL
  col1, col2, col3 = st.columns(3)

  with col1:
    st.markdown(
        f"""
        <div translate="no" class="notranslate" style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; position: relative; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 6px; background-color: #CA8A04;"></div>
            <p style="color: #CA8A04; font-weight: 800; font-size: 0.82rem; margin-bottom: 6px; letter-spacing: 0.03em;">KLASTER 0: PRODUK TERBATAS</p>
            <h3 style="color: #0F172A; font-size: 2rem; font-weight: 800; margin: 0;">{c0_count} Varian</h3>
            <p style="color: #64748B; font-size: 0.8rem; margin-top: 6px; margin-bottom: 0;">Strategi: <b>Safety Stock</b> (Bahan finishing distok terbatas/waspada lonjakan)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with col2:
    st.markdown(
        f"""
        <div translate="no" class="notranslate" style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; position: relative; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 6px; background-color: #16A34A;"></div>
            <p style="color: #16A34A; font-weight: 800; font-size: 0.82rem; margin-bottom: 6px; letter-spacing: 0.03em;">KLASTER 1: STABIL & STOK ADA</p>
            <h3 style="color: #0F172A; font-size: 2rem; font-weight: 800; margin: 0;">{c1_count} Varian</h3>
            <p style="color: #64748B; font-size: 0.8rem; margin-top: 6px; margin-bottom: 0;">Strategi: <b>Make to Stock (MTS)</b> (Bahan cat/amplas selalu siap rutin)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with col3:
    st.markdown(
        f"""
        <div translate="no" class="notranslate" style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; position: relative; overflow: hidden; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <div style="position: absolute; top: 0; left: 0; right: 0; height: 6px; background-color: #DC2626;"></div>
            <p style="color: #DC2626; font-weight: 800; font-size: 0.82rem; margin-bottom: 6px; letter-spacing: 0.03em;">KLASTER 2: RENDAH</p>
            <h3 style="color: #0F172A; font-size: 2rem; font-weight: 800; margin: 0;">{c2_count} Varian</h3>
            <p style="color: #64748B; font-size: 0.8rem; margin-top: 6px; margin-bottom: 0;">Strategi: <b>Make to Order (MTO)</b> (Proses finishing saat ada pesanan)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("---")

  # 5. GRAFIK CENTROID TIME-SERIES
  st.subheader("📈 Grafik Centroid Pola Fluktuasi Penjualan")

  fig = go.Figure()
  cluster_specs = [
      (0, "Centroid Klaster 0 (Produk Terbatas)", "#CA8A04"),
      (1, "Centroid Klaster 1 (Stabil & Stok Ada)", "#16A34A"),
      (2, "Centroid Klaster 2 (Rendah)", "#DC2626"),
  ]

  for c_id, name, color in cluster_specs:
    fig.add_trace(
        go.Scatter(
            x=list(period_cols),
            y=centroids[c_id],
            mode="lines+markers",
            name=name,
            line=dict(color=color, width=3.5),
            marker=dict(size=8, color=color),
        )
    )

  fig.update_layout(
      template="plotly_white",
      height=430,
      xaxis_title="Periode Transaksi (Bulan)",
      yaxis_title="Bentuk Pola Tren (Z-Score)",
      hovermode="x unified",
      legend=dict(
          orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
      ),
      margin=dict(l=20, r=20, t=30, b=20),
  )

  st.plotly_chart(fig, use_container_width=True)

  st.markdown("---")

  # 6. TABEL ANGGOTA & REKOMENDASI PRODUKSI
  st.subheader("📋 Rekomendasi Alokasi Produksi per Varian")

  col_filter, _ = st.columns([2, 2])
  with col_filter:
    selected_cluster = st.selectbox(
        "Filter Klaster:",
        options=[
            "Semua Klaster",
            "Klaster 0 (Produk Terbatas)",
            "Klaster 1 (Stabil & Stok Ada)",
            "Klaster 2 (Rendah)",
        ],
    )

  df_display = df.copy()
  df_display.insert(1, "Cluster", cluster)

  df_display["Kategori Klaster"] = df_display["Cluster"].map({
      0: "Klaster 0 (Produk Terbatas)",
      1: "Klaster 1 (Stabil & Stok Ada)",
      2: "Klaster 2 (Rendah)",
  })

  df_display["Rekomendasi Produksi"] = df_display["Cluster"].map({
      0: "Safety Stock Terbatas",
      1: "Make to Stock (Stok Rutin)",
      2: "Make to Order (Pesanan Masuk)",
  })

  cols = list(df_display.columns)
  cols_reordered = [cols[0]] + [cols[-2], cols[-1], cols[1]] + cols[2:-2]
  df_display = df_display[cols_reordered]

  if selected_cluster != "Semua Klaster":
    df_display = df_display[df_display["Kategori Klaster"] == selected_cluster]

  st.dataframe(df_display, use_container_width=True, hide_index=True)