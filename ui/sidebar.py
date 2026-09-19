import streamlit as st


def sidebar_menu():
  with st.sidebar:
    # Branding Card Box (Persis Desain Vector)
    st.markdown(
        """
        <div class="sidebar-brand-box">
            <div class="brand-title">SISTEM PENDUKUNG KEPUTUSAN PERENCANAAN FINISHING MEBEL</div>
            <div class="brand-subtitle">Decision Support System</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='color: #94A3B8; font-size: 0.75rem; font-weight: 800;"
        " letter-spacing: 0.08em; text-transform: uppercase; margin-bottom:"
        " 10px;'>MENU NAVIGASI</p>",
        unsafe_allow_html=True,
    )

    # Opsi Menu Navigasi
    menu_options = [
        "📊  Dashboard",
        "📈  Analisis DTW",
        "🧩  Clustering",
        "🎯  Rekomendasi",
        "📤  Export",
    ]

    selected = st.radio(
        "Navigation", options=menu_options, label_visibility="collapsed"
    )

    # Mengembalikan string nama menu murni ("Dashboard", "Analisis DTW", dst)
    clean_menu = selected.split("  ")[-1].strip()
    return clean_menu