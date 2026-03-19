"""
Componente de carga de archivos
"""
import streamlit as st
import os
from app.config import KMZ_DIR, TEMP_DIR

def render_file_uploader():
    """Renderiza la sección de carga de archivos"""
    
    st.markdown("""
        <div class="claro-card">
            <h3>📁 Carga de Archivos</h3>
            <p>Suba los archivos necesarios para el análisis de cobertura.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Archivo Excel a Analizar**")
        st.caption("Será renombrado automáticamente a 'Exporte_Dia_Siguiente.xlsx'")
        
        excel_file = st.file_uploader(
            "Seleccione archivo Excel",
            type=['xlsx', 'xls'],
            key="excel_uploader",
            help="Archivo con las órdenes de trabajo a analizar"
        )
        
        if excel_file:
            # Guardar con nombre estándar
            excel_path = os.path.join(TEMP_DIR, "Exporte_Dia_Siguiente.xlsx")
            with open(excel_path, "wb") as f:
                f.write(excel_file.getvalue())
            st.success(f"✅ {excel_file.name} → Exporte_Dia_Siguiente.xlsx")
            st.session_state['excel_path'] = excel_path
    
    with col2:
        st.markdown("**🗺️ Archivo KMZ de Cobertura**")
        st.caption("Mapa de cobertura HFC y FTTH")
        
        kmz_file = st.file_uploader(
            "Seleccione archivo KMZ",
            type=['kmz'],
            key="kmz_uploader",
            help="Archivo KMZ con los polígonos de cobertura"
        )
        
        if kmz_file:
            kmz_path = os.path.join(KMZ_DIR, "Red Fija MAR 2026.kmz")
            with open(kmz_path, "wb") as f:
                f.write(kmz_file.getvalue())
            st.success(f"✅ {kmz_file.name} cargado")
            st.session_state['kmz_path'] = kmz_path
    
    # Verificar estado
    if 'excel_path' in st.session_state and 'kmz_path' in st.session_state:
        st.markdown("""
            <div style="background: #D4EDDA; border-left: 4px solid #28A745; padding: 1rem; border-radius: 5px; margin-top: 1rem;">
                <strong>✅ Listo para analizar</strong><br>
                Ambos archivos cargados correctamente.
            </div>
        """, unsafe_allow_html=True)
        return True
    
    return False