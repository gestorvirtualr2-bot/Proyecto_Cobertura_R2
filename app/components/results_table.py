"""
Tablas de resultados estilizadas
"""
import streamlit as st
import pandas as pd
from app.config import BRAND

def render_summary_cards(summary):
    """Renderiza tarjetas de resumen"""
    st.markdown("### 📊 Resumen del Análisis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Registros",
            value=summary['registros_analizados'],
            delta=f"Filtrados: {summary['registros_filtrados']}"
        )
    
    with col2:
        st.metric(
            label="Con FTTH",
            value=summary['con_ftth'],
            delta=f"{summary['nodos_ftth_unicos']} nodos únicos"
        )
    
    with col3:
        st.metric(
            label="Con HFC",
            value=summary['con_hfc'],
            delta=f"{summary['nodos_hfc_unicos']} nodos únicos"
        )
    
    with col4:
        cobertura_pct = summary['porcentaje_cobertura']
        delta_color = "normal" if cobertura_pct > 80 else "off" if cobertura_pct > 50 else "inverse"
        st.metric(
            label="% Cobertura",
            value=f"{cobertura_pct}%",
            delta=f"{summary['con_ambas']} con ambas tecnologías",
            delta_color=delta_color
        )

def render_data_table(gdf):
    """Renderiza tabla de datos"""
    st.markdown("### 📋 Detalle de Registros")
    
    # Preparar DataFrame para mostrar
    display_df = pd.DataFrame(gdf.drop(columns=['geometry']))
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        cobertura_filter = st.selectbox(
            "Filtrar por Cobertura:",
            ["Todos", "Sí", "No"]
        )
    with col2:
        busqueda = st.text_input("Buscar en resultados:")
    
    # Aplicar filtros
    if cobertura_filter != "Todos":
        display_df = display_df[display_df['COBERTURA'] == cobertura_filter]
    
    if busqueda:
        mask = display_df.astype(str).apply(
            lambda x: x.str.contains(busqueda, case=False, na=False)
        ).any(axis=1)
        display_df = display_df[mask]
    
    # Mostrar tabla
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    return display_df

def render_download_section(gdf):
    """Sección de descarga de resultados"""
    st.markdown("### 💾 Descargar Resultados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel
        df_export = pd.DataFrame(gdf.drop(columns=['geometry']))
        excel_buffer = pd.ExcelWriter('resultado.xlsx', engine='openpyxl')
        df_export.to_excel(excel_buffer, index=False)
        excel_buffer.close()
        
        with open('resultado.xlsx', 'rb') as f:
            st.download_button(
                label="📥 Descargar Excel",
                data=f.read(),
                file_name="Resultado_Cobertura.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        # CSV
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name="Resultado_Cobertura.csv",
            mime="text/csv"
        )