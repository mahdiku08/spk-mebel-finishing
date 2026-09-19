import streamlit as st

from ui.theme import load_theme
from ui.sidebar import sidebar_menu

from ui.dashboard import dashboard_page
from ui.dtw import dtw_page
from ui.clustering import clustering_page
from ui.rekomendation import recommendation_page
from ui.export import export_page


# =====================================================
# KONFIGURASI HALAMAN
# =====================================================

st.set_page_config(

    page_title="SPK Finishing Mebel",

    page_icon="📊",

    layout="wide",

    initial_sidebar_state="expanded"

)

# =====================================================
# LOAD CSS
# =====================================================

load_theme()

# =====================================================
# SESSION STATE
# =====================================================

if "dataset" not in st.session_state:
    st.session_state.dataset = None

if "produk" not in st.session_state:
    st.session_state.produk = None

if "cluster" not in st.session_state:
    st.session_state.cluster = None

if "data_norm" not in st.session_state:
    st.session_state.data_norm = None

if "dbi" not in st.session_state:
    st.session_state.dbi = None

if "model" not in st.session_state:
    st.session_state.model = None

if "rekomendasi" not in st.session_state:
    st.session_state.rekomendasi = None

if "jadwal_finishing" not in st.session_state:
    st.session_state.jadwal_finishing = None

if "dtw_result" not in st.session_state:
    st.session_state.dtw_result = None

# =====================================================
# SIDEBAR
# =====================================================

menu = sidebar_menu()

# =====================================================
# ROUTING
# =====================================================

if menu == "Dashboard":

    dashboard_page()

elif menu == "Analisis DTW":

    dtw_page()

elif menu == "Clustering":

    clustering_page()

elif menu == "Rekomendasi":

    recommendation_page()

elif menu == "Export":

    export_page()