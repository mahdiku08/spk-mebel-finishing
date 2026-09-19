import pandas as pd
import streamlit as st


def recommendation_page():

  # ======================================================
  # 1. HEADER HALAMAN
  # ======================================================
  st.markdown(
      """
    <div class="main-title">
        Rekomendasi Strategi Finishing
    </div>
    <div class="sub-title">
        Rencana prioritas produksi dan alokasi bahan baku finishing berdasarkan karakteristik klaster produk
    </div>
    """,
      unsafe_allow_html=True,
  )

  # ======================================================
  # 2. VALIDASI DATA
  # ======================================================
  if (
      st.session_state.get("cluster") is None
      or st.session_state.get("dataset") is None
  ):
    st.warning(
        "⚠️ Belum ada hasil clustering. Silakan unggah dataset pada menu"
        " **Dashboard** terlebih dahulu."
    )
    return

  df = st.session_state.dataset
  produk_list = st.session_state.produk
  cluster = st.session_state.cluster

  # ======================================================
  # 3. MAPPING STRATEGI PER KLASTER (REVERSED C0 & C1)
  # ======================================================
  rekomendasi_data = []
  angka = df.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").fillna(0)
  rata_bulanan = angka.mean(axis=1)

  for i, prod in enumerate(produk_list):
    c_id = cluster[i]
    avg_val = rata_bulanan.iloc[i]

    if c_id == 0:
      # KLASTER 0: PRODUK TERBATAS (SAFETY STOCK)
      badge_cluster = (
          '<span style="background-color: #FEF9C3; color: #854D0E; padding:'
          ' 4px 12px; border-radius: 12px; font-weight: 700; font-size:'
          ' 0.8rem;">Cluster 0</span>'
      )
      badge_prioritas = (
          '<span style="background-color: #FEF9C3; color: #854D0E; padding:'
          ' 4px 12px; border-radius: 12px; font-weight: 700; font-size:'
          ' 0.8rem;">Terbatas</span>'
      )
      strategi = "Buffer Stok Terbatas (Safety Stock)"
      target_batch = f"{int(round(avg_val * 1.05))} Unit / Bulan"

    elif c_id == 1:
      # KLASTER 1: STABIL & STOK SELALU ADA (MAKE TO STOCK)
      badge_cluster = (
          '<span style="background-color: #DCFCE7; color: #166534; padding:'
          ' 4px 12px; border-radius: 12px; font-weight: 700; font-size:'
          ' 0.8rem;">Cluster 1</span>'
      )
      badge_prioritas = (
          '<span style="background-color: #DCFCE7; color: #166534; padding:'
          ' 4px 12px; border-radius: 12px; font-weight: 700; font-size:'
          ' 0.8rem;">Stabil (Utama)</span>'
      )
      strategi = "Stok Selalu Ready (Make to Stock)"
      target_batch = f"{int(round(avg_val * 1.15))} Unit / Bulan"

    else:
      # KLASTER 2: PERMINTAAN RENDAH (MAKE TO ORDER)
      badge_cluster = (
          '<span style="background-color: #FEE2E2; color: #991B1B; padding:'
          ' 4px 12px; border-radius: 12px; font-weight: 700; font-size:'
          ' 0.8rem;">Cluster 2</span>'
      )
      badge_prioritas = (
          '<span style="background-color: #FEE2E2; color: #991B1B; padding:'
          ' 4px 12px; border-radius: 12px; font-weight: 700; font-size:'
          ' 0.8rem;">Rendah</span>'
      )
      strategi = "Berdasarkan Pesanan (Make to Order)"
      target_batch = "Sesuai PO Client"

    rekomendasi_data.append({
        "Nama Varian Produk": f"<b>{prod}</b>",
        "Klaster": badge_cluster,
        "Prioritas": badge_prioritas,
        "Strategi Stok Bahan": strategi,
        "Rekomendasi Batch": (
            f'<b style="color: #0284C7;">{target_batch}</b>'
        ),
    })

  df_rekomendasi = pd.DataFrame(rekomendasi_data)
  st.session_state.rekomendasi = df_rekomendasi

  # ======================================================
  # 4. TABEL REKOMENDASI
  # ======================================================
  st.subheader("📋 Tabel Matriks Rekomendasi Produksi & Finishing")
  st.write(
      df_rekomendasi.to_html(
          escape=False, index=False, classes="custom-table"
      ),
      unsafe_allow_html=True,
  )

  st.markdown("---")

  # ======================================================
  # 5. CARD PANDUAN STRATEGI
  # ======================================================
  st.subheader("💡 Detail Panduan Strategi per Klaster")

  col1, col2, col3 = st.columns(3)

  with col1:
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span style="background-color: #FEF9C3; color: #854D0E; padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 0.8rem;">Cluster 0</span>
                <h4 style="margin: 0; color: #0F172A; font-size: 1rem; font-weight: 700;">Produk Terbatas</h4>
            </div>
            <ul style="color: #475569; font-size: 0.85rem; padding-left: 18px; margin: 0; line-height: 1.6;">
                <li><b>Strategi:</b> Buffer Stok Terbatas (Safety Stock).</li>
                <li><b>Bahan Baku:</b> Pengadaan bahan finishing secukupnya mengikuti proyeksi tren.</li>
                <li><b>Alokasi Tenaga Kerja:</b> Disesuaikan jadwal saat ada permintaan.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with col2:
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span style="background-color: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 0.8rem;">Cluster 1</span>
                <h4 style="margin: 0; color: #0F172A; font-size: 1rem; font-weight: 700;">Stabil & Stok Ada</h4>
            </div>
            <ul style="color: #475569; font-size: 0.85rem; padding-left: 18px; margin: 0; line-height: 1.6;">
                <li><b>Strategi:</b> Make to Stock (MTS) / Kontinu.</li>
                <li><b>Bahan Baku:</b> Pasokan ampelas, cat, & clear coat selalu siap di gudang.</li>
                <li><b>Alokasi Tenaga Kerja:</b> Lini utama finishing harian.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with col3:
    st.markdown(
        """
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 20px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                <span style="background-color: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 8px; font-weight: 800; font-size: 0.8rem;">Cluster 2</span>
                <h4 style="margin: 0; color: #0F172A; font-size: 1rem; font-weight: 700;">Permintaan Rendah</h4>
            </div>
            <ul style="color: #475569; font-size: 0.85rem; padding-left: 18px; margin: 0; line-height: 1.6;">
                <li><b>Strategi:</b> Make to Order (MTO).</li>
                <li><b>Bahan Baku:</b> Dibeli khusus saat ada <i>Purchase Order</i> (PO) resmi.</li>
                <li><b>Alokasi Tenaga Kerja:</b> Diproses pada slot waktu kustom.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

  # CSS Table Style
  st.markdown(
      """
    <style>
        .custom-table {
            width: 100%; border-collapse: collapse; background-color: #FFFFFF;
            border-radius: 12px; overflow: hidden; border: 1px solid #E2E8F0; margin-top: 10px;
        }
        .custom-table th {
            background-color: #1E293B; color: #FFFFFF; padding: 12px 16px;
            text-align: left; font-size: 0.85rem; font-weight: 700;
        }
        .custom-table td {
            padding: 12px 16px; border-bottom: 1px solid #E2E8F0;
            color: #334155; font-size: 0.88rem;
        }
        .custom-table tr:nth-child(even) { background-color: #F8FAFC; }
    </style>
    """,
      unsafe_allow_html=True,
  )