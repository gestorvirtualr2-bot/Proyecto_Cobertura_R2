"""
Componente de navegación lateral
"""
import streamlit as st
from app.config import BRAND

def render_sidebar():
    """Renderiza la barra lateral de navegación"""
    
    # Logo y título
    st.sidebar.markdown(f"""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 2px solid {BRAND['primary_color']}; margin-bottom: 1rem;">
            <h2 style="color: {BRAND['primary_color']}; margin: 0; font-weight: 700;">📡 CLARO</h2>
            <p style="color: #666; font-size: 0.9rem; margin: 0.5rem 0 0 0;">Sistema de Cobertura</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Menú de navegación
    st.sidebar.markdown("### 🎯 Módulos")
    
    menu_options = {
        "📤 Carga y Análisis": "upload",
        "🔍 Consulta por Nodo": "node_query",
        "📍 Consulta por Coordenadas": "coord_query", 
        "🏠 Consulta por Dirección": "address_query"
    }
    
    selection = st.sidebar.radio(
        "Seleccione módulo:",
        list(menu_options.keys()),
        label_visibility="collapsed"
    )
    
    # Información del sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Información")
    
    with st.sidebar.expander("📊 Estadísticas"):
        if 'analysis_summary' in st.session_state:
            summary = st.session_state['analysis_summary']
            st.metric("Total Analizados", summary.get('registros_analizados', 0))
            st.metric("Con Cobertura", f"{summary.get('porcentaje_cobertura', 0)}%")
        else:
            st.info("Realice un análisis para ver estadísticas")
    
    with st.sidebar.expander("⚙️ Configuración"):
        st.info(f"""
        **Tolerancia:** 50 metros  
        **Sistema:** EPSG:4326  
        **Versión:** 1.0 PRO
        """)
    
    # Footer sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"""
        <div style="text-align: center; font-size: 0.8rem; color: #999;">
            <p>© 2024 Claro Colombia</p>
            <p style="font-size: 0.7rem;">Desarrollado con ❤️</p>
        </div>
    """, unsafe_allow_html=True)
    
    return menu_options[selection]