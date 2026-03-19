"""
Claro Cobertura Pro - Sistema de Análisis Geoespacial
Main Application Entry Point
"""
import streamlit as st
import os
import sys

# Añadir directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.styles import apply_claro_styles, show_header, show_footer
from app.components.sidebar import render_sidebar
from app.components.file_uploader import render_file_uploader
from app.components.map_viewer import render_map, render_single_point_map
from app.components.results_table import render_summary_cards, render_data_table, render_download_section
from app.core.analyzer import CoverageAnalyzer
from app.core.geocoder import ColombiaGeocoder
from app.config import BRAND, KMZ_DIR

# Configuración de página
st.set_page_config(
    page_title="Claro Cobertura Pro",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar estilos
apply_claro_styles()

# Inicializar session state
if 'analyzer' not in st.session_state:
    st.session_state['analyzer'] = None
if 'geocoder' not in st.session_state:
    st.session_state['geocoder'] = ColombiaGeocoder()
if 'kmz_loaded' not in st.session_state:
    st.session_state['kmz_loaded'] = False

def main():
    """Función principal"""
    show_header()
    
    # Renderizar sidebar y obtener selección
    current_module = render_sidebar()
    
    # Módulo: Carga y Análisis
    if current_module == "upload":
        render_upload_module()
    
    # Módulo: Consulta por Nodo
    elif current_module == "node_query":
        render_node_query_module()
    
    # Módulo: Consulta por Coordenadas
    elif current_module == "coord_query":
        render_coord_query_module()
    
    # Módulo: Consulta por Dirección
    elif current_module == "address_query":
        render_address_query_module()
    
    show_footer()

def render_upload_module():
    """Módulo de carga y análisis masivo"""
    st.markdown("""
        <div class="claro-card animate-fade-in">
            <h3>📤 Análisis Masivo de Cobertura</h3>
            <p>Cargue el archivo Excel con las órdenes de trabajo para analizar cobertura FTTH y HFC.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Carga de archivos
    files_ready = render_file_uploader()
    
    if not files_ready:
        st.info("👆 Por favor cargue ambos archivos para continuar")
        return
    
    # Botón de análisis
    if st.button("🚀 INICIAR ANÁLISIS", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(progress, message):
            progress_bar.progress(progress)
            status_text.info(f"⏳ {message}")
        
        try:
            # Inicializar analizador
            kmz_path = st.session_state['kmz_path']
            analyzer = CoverageAnalyzer(kmz_path)
            
            update_progress(5, "Inicializando sistema...")
            
            # Cargar coberturas
            if not analyzer.load_coverages(update_progress):
                st.error("❌ Error al cargar coberturas del KMZ")
                return
            
            # Procesar Excel
            excel_path = st.session_state['excel_path']
            resultado = analyzer.process_excel(excel_path, update_progress)
            
            if not resultado['success']:
                st.error(f"❌ {resultado['error']}")
                return
            
            # Guardar en session state
            st.session_state['analyzer'] = analyzer
            st.session_state['last_result'] = resultado
            st.session_state['analysis_summary'] = resultado['summary']
            st.session_state['kmz_loaded'] = True
            
            update_progress(100, "¡Análisis completado!")
            
            # Mostrar éxito
            st.success("✅ Análisis completado exitosamente")
            
            # Mostrar resumen
            render_summary_cards(resultado['summary'])
            
            # Mostrar mapa
            st.markdown("### 🗺️ Mapa de Cobertura")
            gdf = resultado['gdf']
            render_map(
                gdf_ftth=analyzer.coberturas_ftth,
                gdf_hfc=analyzer.coberturas_hfc,
                gdf_puntos=gdf,
                key="main_map"
            )
            
            # Tabla de resultados
            render_data_table(gdf)
            
            # Descarga
            render_download_section(gdf)
            
        except Exception as e:
            st.error(f"❌ Error durante el análisis: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

def render_node_query_module():
    """Consulta por nombre de nodo"""
    st.markdown("""
        <div class="claro-card animate-fade-in">
            <h3>🔍 Consulta por Nodo</h3>
            <p>Busque un nodo HFC o FTTH por nombre y visualice su polígono de cobertura.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Verificar que hay coberturas cargadas
    if not st.session_state['kmz_loaded']:
        # Intentar cargar desde archivo existente
        kmz_default = os.path.join(KMZ_DIR, "Red Fija MAR 2026.kmz")
        if os.path.exists(kmz_default):
            with st.spinner("Cargando coberturas..."):
                analyzer = CoverageAnalyzer(kmz_default)
                if analyzer.load_coverages():
                    st.session_state['analyzer'] = analyzer
                    st.session_state['kmz_loaded'] = True
                    st.success("Coberturas cargadas automáticamente")
        else:
            st.warning("⚠️ No hay coberturas cargadas. Por favor vaya a 'Carga y Análisis' primero.")
            return
    
    analyzer = st.session_state['analyzer']
    
    # Búsqueda
    col1, col2 = st.columns([3, 1])
    with col1:
        node_search = st.text_input("Nombre del Nodo:", placeholder="Ej: NODO_CENTRO_01")
    with col2:
        search_type = st.selectbox("Tipo:", ["Todos", "FTTH", "HFC"])
    
    if st.button("🔍 BUSCAR NODO", type="primary"):
        if not node_search:
            st.warning("Ingrese un nombre de nodo")
            return
        
        # Buscar en coberturas
        gdf_search = None
        color = "#DA291C"
        
        if search_type in ["Todos", "FTTH"]:
            result = st.session_state['geocoder'].search_node_polygon(
                node_search, analyzer.coberturas_ftth
            )
            if result:
                gdf_search = analyzer.coberturas_ftth[
                    analyzer.coberturas_ftth['nombre'] == result['nombre']
                ]
                color = "#28A745"
                st.success(f"✅ Nodo FTTH encontrado: {result['nombre']}")
        
        if search_type in ["Todos", "HFC"] and gdf_search is None:
            result = st.session_state['geocoder'].search_node_polygon(
                node_search, analyzer.coberturas_hfc
            )
            if result:
                gdf_search = analyzer.coberturas_hfc[
                    analyzer.coberturas_hfc['nombre'] == result['nombre']
                ]
                color = "#0066CC"
                st.success(f"✅ Nodo HFC encontrado: {result['nombre']}")
        
        if gdf_search is None:
            st.error("❌ Nodo no encontrado")
            return
        
        # Calcular centro del polígono
        bounds = result['bounds']
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        
        # Mostrar mapa
        st.markdown("### 📍 Ubicación del Nodo")
        
        import folium
        from streamlit_folium import st_folium
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=15)
        
        # Agregar polígono
        for _, row in gdf_search.iterrows():
            geom = row.geometry
            if geom.geom_type == 'Polygon':
                folium.Polygon(
                    locations=[(y, x) for x, y in geom.exterior.coords],
                    popup=f"<b>{row['nombre']}</b>",
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.3,
                    weight=3
                ).add_to(m)
        
        st_folium(m, width="100%", height=600)
        
        # Información del nodo
        with st.expander("📋 Información Detallada"):
            st.json({
                "Nombre": result['nombre'],
                "Tipo": result['tipo'],
                "Coordenadas Centro": f"{center_lat}, {center_lon}",
                "Bounds": f"{bounds}"
            })

def render_coord_query_module():
    """Consulta por coordenadas"""
    st.markdown("""
        <div class="claro-card animate-fade-in">
            <h3>📍 Consulta por Coordenadas</h3>
            <p>Ingrese latitud y longitud para verificar cobertura en tiempo real.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Verificar coberturas
    if not st.session_state['kmz_loaded']:
        kmz_default = os.path.join(KMZ_DIR, "Red Fija MAR 2026.kmz")
        if os.path.exists(kmz_default):
            with st.spinner("Cargando coberturas..."):
                analyzer = CoverageAnalyzer(kmz_default)
                if analyzer.load_coverages():
                    st.session_state['analyzer'] = analyzer
                    st.session_state['kmz_loaded'] = True
    
    if not st.session_state['kmz_loaded']:
        st.warning("⚠️ No hay coberturas disponibles")
        return
    
    # Inputs de coordenadas
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitud:", value=4.710989, format="%.6f")
    with col2:
        lon = st.number_input("Longitud:", value=-74.072090, format="%.6f")
    
    if st.button("🔍 VERIFICAR COBERTURA", type="primary"):
        from shapely.geometry import Point
        from app.config import TOLERANCIA_GRADOS
        
        punto = Point(lon, lat)
        analyzer = st.session_state['analyzer']
        
        # Buscar cobertura
        res_ftth = analyzer._buscar_nodo(punto, analyzer.coberturas_ftth)
        res_hfc = analyzer._buscar_nodo(punto, analyzer.coberturas_hfc)
        
        tiene_ftth = res_ftth is not None
        tiene_hfc = res_hfc is not None
        
        # Resultados
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if tiene_ftth:
                st.success(f"✅ **FTTH Disponible**\n\nNodo: {res_ftth[0]}")
            else:
                st.error("❌ Sin cobertura FTTH")
        
        with col2:
            if tiene_hfc:
                st.success(f"✅ **HFC Disponible**\n\nNodo: {res_hfc[0]}")
            else:
                st.error("❌ Sin cobertura HFC")
        
        with col3:
            if tiene_ftth or tiene_hfc:
                st.info("✅ **TIENE COBERTURA CLARO**")
            else:
                st.warning("⚠️ **SIN COBERTURA**")
        
        # Mapa
        st.markdown("### 🗺️ Visualización")
        
        # Preparar capas de cobertura encontrada
        gdf_ftth_show = None
        gdf_hfc_show = None
        
        if tiene_ftth:
            gdf_ftth_show = analyzer.coberturas_ftth[
                analyzer.coberturas_ftth['nombre'] == res_ftth[0]
            ]
        
        if tiene_hfc:
            gdf_hfc_show = analyzer.coberturas_hfc[
                analyzer.coberturas_hfc['nombre'] == res_hfc[0]
            ]
        
        render_single_point_map(lat, lon, 
                               coverage_gdf=gdf_ftth_show if gdf_ftth_show is not None else gdf_hfc_show)

def render_address_query_module():
    """Consulta por dirección"""
    st.markdown("""
        <div class="claro-card animate-fade-in">
            <h3>🏠 Consulta por Dirección</h3>
            <p>Ingrese una dirección colombiana para geocodificar y verificar cobertura.</p>
            <p><small>Formatos: <code>Calle 80 # 22-10</code>, <code>Carrera 15 # 45-30</code>, <code>AV 68 # 25-10</code></small></p>
        </div>
    """, unsafe_allow_html=True)
    
    # Verificar coberturas
    if not st.session_state['kmz_loaded']:
        kmz_default = os.path.join(KMZ_DIR, "Red Fija MAR 2026.kmz")
        if os.path.exists(kmz_default):
            with st.spinner("Cargando coberturas..."):
                analyzer = CoverageAnalyzer(kmz_default)
                if analyzer.load_coverages():
                    st.session_state['analyzer'] = analyzer
                    st.session_state['kmz_loaded'] = True
    
    if not st.session_state['kmz_loaded']:
        st.warning("⚠️ No hay coberturas disponibles")
        return
    
    # Input de dirección
    address = st.text_input("Dirección:", placeholder="Ej: Calle 80 # 22-10, Bogotá")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        search_btn = st.button("🔍 BUSCAR Y VERIFICAR", type="primary", use_container_width=True)
    
    if search_btn and address:
        with st.spinner("Geocodificando dirección..."):
            result = st.session_state['geocoder'].geocode_address(address)
        
        if not result['success']:
            st.error(f"❌ {result['error']}")
            return
        
        # Mostrar resultado de geocodificación
        st.success(f"✅ Dirección encontrada: {result['address']}")
        
        lat, lon = result['latitude'], result['longitude']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Latitud", f"{lat:.6f}")
        with col2:
            st.metric("Longitud", f"{lon:.6f}")
        
        # Verificar cobertura
        from shapely.geometry import Point
        from app.config import TOLERANCIA_GRADOS
        
        punto = Point(lon, lat)
        analyzer = st.session_state['analyzer']
        
        res_ftth = analyzer._buscar_nodo(punto, analyzer.coberturas_ftth)
        res_hfc = analyzer._buscar_nodo(punto, analyzer.coberturas_hfc)
        
        tiene_ftth = res_ftth is not None
        tiene_hfc = res_hfc is not None
        
        # Resultados de cobertura
        st.markdown("### 📡 Resultado de Cobertura")
        
        cols = st.columns(3)
        with cols[0]:
            st.metric("FTTH", "✅ Sí" if tiene_ftth else "❌ No", 
                     delta=res_ftth[0] if tiene_ftth else None)
        with cols[1]:
            st.metric("HFC", "✅ Sí" if tiene_hfc else "❌ No",
                     delta=res_hfc[0] if tiene_hfc else None)
        with cols[2]:
            cobertura = "✅ CON COBERTURA" if (tiene_ftth or tiene_hfc) else "❌ SIN COBERTURA"
            st.metric("Estado", cobertura)
        
        # Mapa
        st.markdown("### 🗺️ Ubicación en Mapa")
        
        gdf_ftth_show = None
        gdf_hfc_show = None
        
        if tiene_ftth:
            gdf_ftth_show = analyzer.coberturas_ftth[
                analyzer.coberturas_ftth['nombre'] == res_ftth[0]
            ]
        
        if tiene_hfc:
            gdf_hfc_show = analyzer.coberturas_hfc[
                analyzer.coberturas_hfc['nombre'] == res_hfc[0]
            ]
        
        # Combinar coberturas para mostrar
        gdf_show = None
        if gdf_ftth_show is not None and not gdf_ftth_show.empty:
            gdf_show = gdf_ftth_show
        elif gdf_hfc_show is not None and not gdf_hfc_show.empty:
            gdf_show = gdf_hfc_show
        
        render_single_point_map(lat, lon, coverage_gdf=gdf_show, 
                               title=f"Dirección: {address}")

if __name__ == "__main__":
    main()