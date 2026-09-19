import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from tslearn.metrics import dtw, dtw_path


def dtw_page():

    # ======================================================
    # 1. HEADER HALAMAN
    # ======================================================
    st.markdown(
        """
    <div class="main-title">
        Analisis Dynamic Time Warping (DTW)
    </div>
    <div class="sub-title">
        Perhitungan jarak kemiripan pola time-series antar varian produk finishing mebel
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ======================================================
    # 2. VALIDASI DATASET
    # ======================================================
    if (
        st.session_state.get("dataset") is None
        or st.session_state.get("data_norm") is None
    ):
        st.warning(
            "⚠️ Belum ada dataset yang diunggah. Silakan unggah dataset pada"
            " menu **Dashboard** terlebih dahulu."
        )
        return

    df = st.session_state.dataset
    produk_list = st.session_state.produk
    data_norm = st.session_state.data_norm.reshape(
        st.session_state.data_norm.shape[0], -1
    )
    period_cols = list(df.columns[1:])

    # ======================================================
    # 3. CONTROL CARD: PILIH PRODUK A & PRODUK B
    # ======================================================
    st.markdown(
        """
    <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px 24px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
        <h4 style="color: #1E293B; font-size: 1rem; font-weight: 700; margin-top: 0; margin-bottom: 16px;">🔍 Pemilihan Pasangan Produk untuk Alignment DTW</h4>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        idx_a = st.selectbox(
            "PILIH PRODUK A (ACUAN):",
            options=range(len(produk_list)),
            format_func=lambda x: produk_list[x],
            index=0,
        )

    with col_b:
        default_b_idx = 1 if len(produk_list) > 1 else 0
        idx_b = st.selectbox(
            "PILIH PRODUK B (PEMBANDING):",
            options=range(len(produk_list)),
            format_func=lambda x: produk_list[x],
            index=default_b_idx,
        )

    ts_a = data_norm[idx_a]
    ts_b = data_norm[idx_b]

    # Kalkulasi DTW Path & Distance
    path, dtw_dist = dtw_path(ts_a, ts_b)

    st.markdown("---")

    # ======================================================
    # 4. GRAFIK VISUALISASI ALIGNMENT DTW
    # ======================================================
    st.subheader("📈 Visualisasi Alignment DTW (Time Series Alignment)")

    fig = go.Figure()

    # Seri Produk A (Solid Line Blue)
    fig.add_trace(
        go.Scatter(
            x=period_cols,
            y=ts_a,
            mode="lines+markers",
            name=f"Produk A: {produk_list[idx_a]}",
            line=dict(color="#0284C7", width=3.5),
            marker=dict(size=7, color="#0284C7"),
        )
    )

    # Seri Produk B (Dashed Line Amber)
    fig.add_trace(
        go.Scatter(
            x=period_cols,
            y=ts_b,
            mode="lines+markers",
            name=f"Produk B: {produk_list[idx_b]}",
            line=dict(color="#F59E0B", width=3.5, dash="dash"),
            marker=dict(size=7, color="#F59E0B"),
        )
    )

    # Warping Path Lines (Garis Penghubung Titik Alignment)
    for p1, p2 in path:
        fig.add_trace(
            go.Scatter(
                x=[period_cols[p1], period_cols[p2]],
                y=[ts_a[p1], ts_b[p2]],
                mode="lines",
                line=dict(color="#94A3B8", width=1.2, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            )
        )

    fig.update_layout(
        template="plotly_white",
        height=420,
        xaxis_title="Periode Penjualan",
        yaxis_title="Nilai Ter-normalisasi (Z-Score)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ======================================================
    # 5. TABEL MATRIKS JARAK DTW (DENGAN PERSENTASE KEMIRIPAN)
    # ======================================================
    st.subheader("📊 Matriks Jarak DTW & Persentase Kemiripan")

    matrix_data_raw = []
    distances = []
    n_samples = min(len(produk_list), 10)  # Sampel 10 produk pertama

    # 1. Hitung seluruh jarak DTW antar sampel
    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            dist_val = dtw(data_norm[i], data_norm[j])
            distances.append(dist_val)
            matrix_data_raw.append((produk_list[i], produk_list[j], dist_val))

    if len(distances) > 0:
        d_min = min(distances)
        d_max = max(distances)
    else:
        d_min, d_max = 0.0, 1.0

    # 2. Format Data & Hitung Persentase Kemiripan
    matrix_data = []
    for prod_a, prod_b, dist_val in matrix_data_raw:

        # Formula Persentase Kemiripan Relative Min-Max (0 - 100%)
        if d_max != d_min:
            similarity_pct = (1.0 - ((dist_val - d_min) / (d_max - d_min))) * 100.0
        else:
            similarity_pct = 100.0

        # Pengkategorian Berdasarkan Ambang Batas Persentase Kemiripan:
        # > 70.0%       : Tinggi
        # 40.1% - 70.0% : Sedang
        # <= 40.0%      : Rendah
        if similarity_pct > 70.0:
            badge_style = (
                f'<span style="background-color: #DCFCE7; color: #166534;'
                " padding: 4px 12px; border-radius: 12px; font-weight: 700;"
                f' font-size: 0.8rem;">Tinggi ({similarity_pct:.1f}%)</span>'
            )
        elif similarity_pct > 40.0:
            badge_style = (
                f'<span style="background-color: #FEF9C3; color: #854D0E;'
                " padding: 4px 12px; border-radius: 12px; font-weight: 700;"
                f' font-size: 0.8rem;">Sedang ({similarity_pct:.1f}%)</span>'
            )
        else:
            badge_style = (
                f'<span style="background-color: #FEE2E2; color: #991B1B;'
                " padding: 4px 12px; border-radius: 12px; font-weight: 700;"
                f' font-size: 0.8rem;">Rendah ({similarity_pct:.1f}%)</span>'
            )

        matrix_data.append({
            "Pasangan Produk": f"{prod_a} <b>vs</b> {prod_b}",
            "Jarak DTW (Score)": f"{dist_val:.4f}",
            "Tingkat Kemiripan (%)": badge_style,
        })

    df_matrix = pd.DataFrame(matrix_data)

    # Tampilkan Tabel HTML Kustom
    st.write(
        df_matrix.to_html(escape=False, index=False, classes="custom-table"),
        unsafe_allow_html=True,
    )