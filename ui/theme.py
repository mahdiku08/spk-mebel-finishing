import streamlit as st


def load_theme():
  st.markdown(
      """
    <style>
        /* =====================================================
           1. FONTS & MAIN LAYOUT (MENCEGAH TITLE TERPOTONG)
        ===================================================== */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        .block-container {
            padding-top: 2.2rem !important;
            padding-bottom: 3rem !important;
            max-width: 1200px !important;
        }
        
        .main-title, h1 {
            font-size: 2.1rem !important;
            font-weight: 800 !important;
            color: #0F172A !important;
            line-height: 1.35 !important;
            margin-top: 0px !important;
            margin-bottom: 0.3rem !important;
            padding-top: 6px !important;
            letter-spacing: -0.02em;
        }
        
        .sub-title {
            font-size: 0.95rem !important;
            color: #475569 !important;
            line-height: 1.5 !important;
            margin-bottom: 1.5rem !important;
            font-weight: 500 !important;
        }

        /* =====================================================
           2. STREAMLIT HEADER / TOP NAVBAR STYLING
        ===================================================== */
        /* Sembunyikan garis pelangi bawaan Streamlit di paling atas */
        div[data-testid="stDecoration"] {
            display: none !important;
        }

        /* Styling Header Bar Atas */
        header[data-testid="stHeader"] {
            background-color: rgba(15, 23, 42, 0.95) !important;
            backdrop-filter: blur(8px) !important;
            border-bottom: 1px solid #1E293B !important;
            height: 3.5rem !important;
        }

        /* Menyesuaikan Warna Ikon Menu Titik Tiga / Sidebar Toggle di Navbar */
        header[data-testid="stHeader"] button,
        header[data-testid="stHeader"] svg {
            color: #F8FAFC !important;
            fill: #F8FAFC !important;
        }

        /* Status Indicator Running Animation */
        div[data-testid="stStatusWidget"] {
            color: #38BDF8 !important;
        }

        /* =====================================================
           3. SIDEBAR DARK THEME (#0F172A)
        ===================================================== */
        [data-testid="stSidebar"] {
            background-color: #0F172A !important;
        }

        [data-testid="stSidebar"] > div:first-child {
            background-color: #0F172A !important;
        }

        .sidebar-brand-box {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }
        
        .brand-title {
            color: #FFFFFF !important;
            font-size: 0.82rem !important;
            font-weight: 800 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            line-height: 1.4 !important;
        }
        
        .brand-subtitle {
            color: #38BDF8 !important;
            font-size: 0.75rem !important;
            font-weight: 700 !important;
            margin-top: 4px;
        }

        /* =====================================================
           4. NAVIGASI (TETAP DIAM, SEJAJAR & TIDAK BERGESER)
        ===================================================== */
        /* Sembunyikan titik radio button bawaan */
        [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }

        /* Target Semua Label Navigasi Biasa (Transparan & Stabil) */
        [data-testid="stSidebar"] div[role="radiogroup"] label {
            background: transparent !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
            margin-bottom: 6px !important;
            
            /* Border transparan seimbang agar tidak meloncat */
            border: 2px solid transparent !important;
            border-left: 6px solid transparent !important;
            
            cursor: pointer !important;
            transform: none !important;
            transition: background-color 0.15s ease !important;
        }

        /* Memaksa Teks Terang Kontras */
        [data-testid="stSidebar"] div[role="radiogroup"] label *,
        [data-testid="stSidebar"] div[role="radiogroup"] label p,
        [data-testid="stSidebar"] div[role="radiogroup"] label span {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            opacity: 1 !important;
            margin: 0 !important;
        }

        /* Hover Pasif (Sorot Latar Tipis, Diam Tegas) */
        [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background-color: rgba(255, 255, 255, 0.08) !important;
            transform: none !important;
            box-shadow: none !important;
        }

        /* =====================================================
           5. MENU AKTIF (GRADIEN BLUE-CYAN, INDIKATOR KIRI, DIAM)
        ===================================================== */
        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
            background: linear-gradient(90deg, #0284C7 0%, #38BDF8 100%) !important;
            border: 2px solid #7DD3FC !important;
            border-left: 6px solid #FFFFFF !important;
            
            transform: none !important;
            box-shadow: 0 4px 16px rgba(56, 189, 248, 0.4) !important;
        }

        [data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] * {
            color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important;
            font-weight: 800 !important;
            text-shadow: 0px 1px 3px rgba(0, 0, 0, 0.6) !important;
        }

        /* =====================================================
           6. METRIC CARDS STYLING
        ===================================================== */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-weight: 600 !important;
            font-size: 0.85rem !important;
        }

        div[data-testid="stMetricValue"] {
            color: #0F172A !important;
            font-weight: 800 !important;
        }
    </style>
    """,
      unsafe_allow_html=True,
  )