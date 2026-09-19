import io
import re
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
import streamlit as st

# ==========================================================
# 1. HELPER FUNGSI PDF & CLEANING
# ==========================================================


def clean_html_tags(text):
  """Menghapus tag HTML (seperti <span>, <b>, <i>) dari string."""
  if not isinstance(text, str):
    return str(text)
  return re.sub(r"<[^>]*>", "", text).strip()


def generate_pdf_report(df, jml_produk, jml_cluster, silhouette_val):
  """Membuat dokumen PDF resmi A4 menggunakan metrik Silhouette Score."""
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(
      buffer,
      pagesize=A4,
      rightMargin=30,
      leftMargin=30,
      topMargin=30,
      bottomMargin=30,
  )
  elements = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      "DocTitle",
      parent=styles["Heading1"],
      fontSize=13,
      leading=16,
      textColor=colors.HexColor("#1E293B"),
      alignment=1,
      fontName="Helvetica-Bold",
  )
  subtitle_style = ParagraphStyle(
      "DocSubTitle",
      parent=styles["Normal"],
      fontSize=8.5,
      leading=11,
      textColor=colors.HexColor("#64748B"),
      alignment=1,
      spaceAfter=12,
  )
  section_style = ParagraphStyle(
      "SectionHeader",
      parent=styles["Heading2"],
      fontSize=10,
      leading=12,
      textColor=colors.HexColor("#0F172A"),
      spaceBefore=8,
      spaceAfter=8,
      fontName="Helvetica-Bold",
  )
  cell_style = ParagraphStyle(
      "TableCell",
      parent=styles["Normal"],
      fontSize=7.5,
      leading=9.5,
      textColor=colors.HexColor("#334155"),
  )
  header_cell_style = ParagraphStyle(
      "HeaderTableCell",
      parent=styles["Normal"],
      fontSize=7.5,
      leading=9.5,
      textColor=colors.white,
      fontName="Helvetica-Bold",
  )

  # Kop Laporan
  elements.append(
      Paragraph("LAPORAN HASIL ANALISIS & REKOMENDASI FINISHING", title_style)
  )
  elements.append(
      Paragraph(
          "Sistem Pendukung Keputusan Perencanaan Produksi Finishing Mebel",
          subtitle_style,
      )
  )
  elements.append(
      HRFlowable(
          width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=10
      )
  )

  # Ringkasan Metrik (Silhouette Score)
  summary_data = [
      [
          Paragraph("<b>Jumlah Produk</b>", cell_style),
          Paragraph("<b>Jumlah Cluster</b>", cell_style),
          Paragraph("<b>Silhouette Score</b>", cell_style),
      ],
      [
          Paragraph(f"{jml_produk} Varian", cell_style),
          Paragraph(f"{jml_cluster} Klaster", cell_style),
          Paragraph(f"{silhouette_val:.4f}", cell_style),
      ],
  ]
  summary_table = Table(summary_data, colWidths=[175, 175, 185])
  summary_table.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
          ("ALIGN", (0, 0), (-1, -1), "CENTER"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
          ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
      ])
  )
  elements.append(summary_table)
  elements.append(Spacer(1, 10))

  # Tabel Rekomendasi
  elements.append(
      Paragraph("Detail Hasil Cluster dan Rekomendasi", section_style)
  )
  df_clean = df.copy()
  for col in df_clean.columns:
    df_clean[col] = df_clean[col].apply(clean_html_tags)

  table_data = [
      [Paragraph(str(col), header_cell_style) for col in df_clean.columns]
  ]
  for _, row in df_clean.iterrows():
    table_data.append([Paragraph(str(val), cell_style) for val in row.values])

  rec_table = Table(table_data, colWidths=[140, 65, 75, 155, 100.5])
  rec_table.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
          (
              "ROWBACKGROUNDS",
              (0, 1),
              (-1, -1),
              [colors.white, colors.HexColor("#F8FAFC")],
          ),
          ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
      ])
  )
  elements.append(rec_table)

  doc.build(elements)
  buffer.seek(0)
  return buffer.getvalue()


# ==========================================================
# 2. HALAMAN EXPORT VIEW
# ==========================================================


def export_page():
  st.markdown(
      """
    <div style="margin-bottom: 24px;">
        <h2 style="color: #0F172A; font-weight: 800; margin-bottom: 6px;">Export Hasil Analisis</h2>
        <p style="color: #64748B; font-size: 0.95rem; margin: 0;">
            Mengunduh hasil analisis clustering dan rekomendasi dalam format Dokumen PDF resmi maupun data CSV
        </p>
    </div>
    """,
      unsafe_allow_html=True,
  )

  if (
      st.session_state.get("rekomendasi") is None
      or st.session_state.get("cluster") is None
  ):
    st.warning(
        "⚠️ Belum ada hasil analisis yang dapat diekspor. Silakan unggah dataset"
        " di menu **Dashboard** terlebih dahulu."
    )
    return

  rekomendasi = st.session_state.rekomendasi
  cluster = st.session_state.cluster
  produk = st.session_state.produk
  silhouette = st.session_state.get("silhouette", 0.0)

  # 3 Kartu Ringkasan Metrik (Dilindungi dari Google Translate Otomatis)
  m1, m2, m3 = st.columns(3)

  with m1:
    st.markdown(
        f"""
        <div translate="no" class="notranslate" style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <p style="color: #64748B; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">Jumlah Produk</p>
            <h3 style="color: #0F172A; font-size: 1.8rem; font-weight: 800; margin: 0;">{len(produk)} <span style="font-size: 0.85rem; font-weight: 600; color: #64748B;">Varian</span></h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with m2:
    st.markdown(
        f"""
        <div translate="no" class="notranslate" style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <p style="color: #64748B; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">Jumlah Cluster</p>
            <h3 style="color: #0F172A; font-size: 1.8rem; font-weight: 800; margin: 0;">{len(set(cluster))} <span style="font-size: 0.85rem; font-weight: 600; color: #64748B;">Klaster</span></h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

  with m3:
    st.markdown(
        f"""
        <div translate="no" class="notranslate" style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
            <p style="color: #64748B; font-size: 0.85rem; font-weight: 600; margin-bottom: 6px;">Silhouette Score</p>
            <h3 style="color: #0284C7; font-size: 1.8rem; font-weight: 800; margin: 0;">{silhouette:.4f}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("<br>", unsafe_allow_html=True)
  st.subheader("📋 Preview Tabel Rekomendasi")
  st.markdown(
      f"""
    <div translate="no" class="notranslate" lang="id">
        {rekomendasi.to_html(escape=False, index=False, classes="custom-table")}
    </div>
    """,
      unsafe_allow_html=True,
  )

  st.markdown("---")
  st.subheader("📥 Unduh Berkas Hasil Analisis")

  col_pdf, col_csv = st.columns(2)

  with col_pdf:
    pdf_bytes = generate_pdf_report(
        df=rekomendasi,
        jml_produk=len(produk),
        jml_cluster=len(set(cluster)),
        silhouette_val=silhouette,
    )
    st.download_button(
        label="📄 Download Laporan PDF (.pdf)",
        data=pdf_bytes,
        file_name="Hasil_Rekomendasi_Finishing.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

  with col_csv:
    df_csv_clean = rekomendasi.copy()
    for col in df_csv_clean.columns:
      df_csv_clean[col] = df_csv_clean[col].apply(clean_html_tags)
    csv_data = df_csv_clean.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📊 Download Data CSV (.csv)",
        data=csv_data,
        file_name="Hasil_Rekomendasi_Finishing.csv",
        mime="text/csv",
        use_container_width=True,
    )