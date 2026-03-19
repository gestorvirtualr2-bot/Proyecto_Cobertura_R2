"""
Visualizador de mapas interactivos
"""
import streamlit as st
import folium
from folium.plugins import Draw, Fullscreen, MarkerCluster
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point
from app.config import BRAND

def create_base_map(center_lat=4.570868, center_lon=-74.297333, zoom=6):
    """Crea mapa base de Colombia"""
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom,
        tiles="OpenStreetMap"
    )
    
    # Agregar capas adicionales
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satélite",
        overlay=False,
        control=True
    ).add_to(m)
    
    # Controles
    Fullscreen().add_to(m)
    
    return m

def add_coverage_layer(m, gdf, color, name):
    """Agrega capa de cobertura al mapa"""
    if gdf is None or gdf.empty:
        return m
    
    feature_group = folium.FeatureGroup(name=name)
    
    for _, row in gdf.iterrows():
        try:
            geom = row.geometry
            if geom is None:
                continue
            
            # Estilo según tipo
            fill_color = color
            if 'tipo' in row:
                if 'Neutra' in str(row['tipo']):
                    fill_color = '#FF6B6B'
                elif 'Propio' in str(row['tipo']):
                    fill_color = '#4ECDC4'
            
            # Agregar polígono
            if geom.geom_type == 'Polygon':
                folium.Polygon(
                    locations=[(y, x) for x, y in geom.exterior.coords],
                    popup=f"<b>{row['nombre']}</b><br>Tipo: {row.get('tipo', 'N/A')}",
                    color=color,
                    fill=True,
                    fill_color=fill_color,
                    fill_opacity=0.3,
                    weight=2
                ).add_to(feature_group)
            elif geom.geom_type == 'MultiPolygon':
                for poly in geom.geoms:
                    folium.Polygon(
                        locations=[(y, x) for x, y in poly.exterior.coords],
                        popup=f"<b>{row['nombre']}</b><br>Tipo: {row.get('tipo', 'N/A')}",
                        color=color,
                        fill=True,
                        fill_color=fill_color,
                        fill_opacity=0.3,
                        weight=2
                    ).add_to(feature_group)
        except:
            continue
    
    feature_group.add_to(m)
    return m

def add_points_layer(m, gdf, color=BRAND['primary_color']):
    """Agrega capa de puntos analizados"""
    if gdf is None or gdf.empty:
        return m
    
    marker_cluster = MarkerCluster(name="Puntos Analizados")
    
    for _, row in gdf.iterrows():
        try:
            punto = row.geometry
            if punto is None:
                continue
            
            # Color según cobertura
            icon_color = 'green' if row.get('COBERTURA') == 'Sí' else 'red'
            
            # Popup con información
            popup_html = f"""
                <div style="font-family: Arial; min-width: 200px;">
                    <h4 style="color: {BRAND['primary_color']}; margin-bottom: 10px;">📍 Punto Analizado</h4>
                    <table style="width: 100%; font-size: 12px;">
                        <tr><td><b>Lat:</b></td><td>{punto.y:.6f}</td></tr>
                        <tr><td><b>Lon:</b></td><td>{punto.x:.6f}</td></tr>
                        <tr><td><b>Cobertura:</b></td><td>{row.get('COBERTURA', 'N/A')}</td></tr>
                        <tr><td><b>Nodo FTTH:</b></td><td>{row.get('NODO_FTTH', 'N/A') or 'N/A'}</td></tr>
                        <tr><td><b>Nodo HFC:</b></td><td>{row.get('NODO_HFC', 'N/A') or 'N/A'}</td></tr>
                    </table>
                </div>
            """
            
            folium.Marker(
                location=[punto.y, punto.x],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=icon_color, icon='signal', prefix='fa')
            ).add_to(marker_cluster)
            
        except:
            continue
    
    marker_cluster.add_to(m)
    return m

def render_map(gdf_ftth=None, gdf_hfc=None, gdf_puntos=None, 
               center=None, zoom=6, height=600, key="map"):
    """Renderiza el mapa completo"""
    
    # Determinar centro
    if center:
        center_lat, center_lon = center
    elif gdf_puntos is not None and not gdf_puntos.empty:
        bounds = gdf_puntos.total_bounds
        center_lat = (bounds[1] + bounds[3]) / 2
        center_lon = (bounds[0] + bounds[2]) / 2
        zoom = 12
    else:
        center_lat, center_lon = 4.570868, -74.297333
    
    m = create_base_map(center_lat, center_lon, zoom)
    
    # Agregar capas
    if gdf_ftth is not None:
        m = add_coverage_layer(m, gdf_ftth, '#DA291C', 'FTTH (Fibra)')
    
    if gdf_hfc is not None:
        m = add_coverage_layer(m, gdf_hfc, '#0066CC', 'HFC (Cable)')
    
    if gdf_puntos is not None:
        m = add_points_layer(m, gdf_puntos)
    
    # Control de capas
    folium.LayerControl().add_to(m)
    
    # Mostrar en Streamlit
    return st_folium(m, width="100%", height=height, returned_objects=[], key=key)

def render_single_point_map(lat, lon, coverage_gdf=None, title="Ubicación Consultada"):
    """Renderiza mapa con un punto específico"""
    m = folium.Map(location=[lat, lon], zoom_start=16)
    
    # Agregar punto de consulta
    folium.Marker(
        [lat, lon],
        popup=title,
        icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
    ).add_to(m)
    
    # Círculo de tolerancia (50m)
    folium.Circle(
        [lat, lon],
        radius=50,
        popup="Tolerancia: 50 metros",
        color="#DA291C",
        fill=True,
        fill_opacity=0.1
    ).add_to(m)
    
    # Agregar cobertura si existe
    if coverage_gdf is not None:
        m = add_coverage_layer(m, coverage_gdf, '#28A745', 'Cobertura Encontrada')
    
    return st_folium(m, width="100%", height=500, returned_objects=[])