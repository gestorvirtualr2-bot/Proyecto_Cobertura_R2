"""
Motor de análisis de cobertura - Adaptación del código original
"""
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from app.config import ACTIVIDADES_VALIDAS, TOLERANCIA_GRADOS
from app.core.kmz_parser import KMZParser

class CoverageAnalyzer:
    """Analizador de cobertura basado en el código original funcional"""
    
    def __init__(self, kmz_path):
        self.kmz_path = kmz_path
        self.coberturas_ftth = None
        self.coberturas_hfc = None
        self.parser = None
        
    def load_coverages(self, progress_callback=None):
        """Carga las coberturas del KMZ"""
        if progress_callback:
            progress_callback(10, "Extrayendo archivo KMZ...")
            
        self.parser = KMZParser(self.kmz_path)
        self.coberturas_ftth, self.coberturas_hfc = self.parser.get_all_coverages()
        
        if progress_callback:
            ftth_count = len(self.coberturas_ftth) if self.coberturas_ftth is not None else 0
            hfc_count = len(self.coberturas_hfc) if self.coberturas_hfc is not None else 0
            progress_callback(30, f"Coberturas cargadas: FTTH={ftth_count}, HFC={hfc_count}")
        
        return True
    
    def process_excel(self, excel_path, progress_callback=None):
        """
        Procesa el archivo Excel y retorna resultados
        """
        # 1. Leer Excel
        if progress_callback:
            progress_callback(35, "Leyendo archivo Excel...")
            
        df = pd.read_excel(excel_path)
        total_registros = len(df)
        
        # 2. Filtrar
        if progress_callback:
            progress_callback(40, "Filtrando registros válidos...")
            
        df["Tipo de Actividad"] = df["Tipo de Actividad"].astype(str).str.strip().str.upper()
        df["Estado"] = df["Estado"].astype(str).str.strip().str.upper()
        
        df_filtered = df[
            (df["Tipo de Actividad"].isin([a.upper() for a in ACTIVIDADES_VALIDAS])) &
            (df["Estado"] == "PENDIENTE") &
            (df["Coordenada X"].notna()) & (df["Coordenada X"] != "") &
            (df["Coordenada Y"].notna()) & (df["Coordenada Y"] != "")
        ].copy()
        
        registros_filtrados = len(df_filtered)
        
        if registros_filtrados == 0:
            return {
                "success": False,
                "error": "No hay registros válidos para analizar",
                "total_registros": total_registros,
                "registros_filtrados": 0
            }
        
        # 3. Crear geometrías
        if progress_callback:
            progress_callback(50, "Creando geometrías de puntos...")
            
        df_filtered["LATITUD"] = pd.to_numeric(df_filtered["Coordenada Y"], errors="coerce")
        df_filtered["LONGITUD"] = pd.to_numeric(df_filtered["Coordenada X"], errors="coerce")
        df_filtered = df_filtered[
            (df_filtered["LATITUD"].notna()) & 
            (df_filtered["LONGITUD"].notna())
        ].copy()
        
        geometry = [
            Point(lon, lat) if pd.notnull(lat) and pd.notnull(lon) else None
            for lon, lat in zip(df_filtered["LONGITUD"], df_filtered["LATITUD"])
        ]
        
        gdf_puntos = gpd.GeoDataFrame(df_filtered, geometry=geometry, crs="EPSG:4326")
        
        # 4. Análisis de cobertura
        if progress_callback:
            progress_callback(60, "Analizando cobertura FTTH...")
            
        resultados = self._analyze_points(gdf_puntos, progress_callback)
        
        # 5. Preparar resumen
        resumen = self._generate_summary(resultados, total_registros, registros_filtrados)
        
        return {
            "success": True,
            "data": resultados,
            "summary": resumen,
            "gdf": gdf_puntos
        }
    
    def _analyze_points(self, gdf_puntos, progress_callback=None):
        """Analiza cobertura punto por punto"""
        nodo_hfc_result = []
        nodo_ftth_result = []
        
        total = len(gdf_puntos)
        
        for i, (idx, row) in enumerate(gdf_puntos.iterrows()):
            punto = row.geometry
            
            if punto is None or punto.is_empty:
                nodo_hfc_result.append(None)
                nodo_ftth_result.append(None)
                continue
            
            # Buscar FTTH
            res_ftth = self._buscar_nodo(punto, self.coberturas_ftth)
            nodo_ftth_result.append(res_ftth[0] if res_ftth else None)
            
            # Buscar HFC
            res_hfc = self._buscar_nodo(punto, self.coberturas_hfc)
            nodo_hfc_result.append(res_hfc[0] if res_hfc else None)
            
            # Progreso
            if progress_callback and (i + 1) % max(1, total // 10) == 0:
                progress = 60 + int((i / total) * 30)
                progress_callback(progress, f"Analizando punto {i+1}/{total}...")
        
        # Agregar resultados al GeoDataFrame
        gdf_puntos["NODO_HFC"] = nodo_hfc_result
        gdf_puntos["NODO_FTTH"] = nodo_ftth_result
        gdf_puntos["COBERTURA"] = gdf_puntos.apply(
            lambda r: "Sí" if (r["NODO_HFC"] or r["NODO_FTTH"]) else "No", 
            axis=1
        )
        
        return gdf_puntos
    
    def _buscar_nodo(self, punto, coberturas, tolerancia=TOLERANCIA_GRADOS):
        """Busca nodo con tolerancia"""
        if coberturas is None or coberturas.empty:
            return None
        
        nodo_encontrado = None
        distancia_minima = float('inf')
        
        for _, pol in coberturas.iterrows():
            try:
                geom = pol.geometry
                if geom is None or geom.is_empty:
                    continue
                
                # Dentro del polígono
                if geom.contains(punto):
                    return (pol["nombre"], 0)
                
                # Fuera, calcular distancia
                distancia = geom.distance(punto)
                if distancia <= tolerancia and distancia < distancia_minima:
                    distancia_minima = distancia
                    nodo_encontrado = pol["nombre"]
                    
            except:
                continue
        
        return (nodo_encontrado, distancia_minima) if nodo_encontrado else None
    
    def _generate_summary(self, gdf, total_registros, registros_filtrados):
        """Genera resumen estadístico"""
        con_ftth = gdf["NODO_FTTH"].notna().sum()
        con_hfc = gdf["NODO_HFC"].notna().sum()
        
        # Contar ambas (donde ambos no son nulos)
        con_ambas = ((gdf["NODO_FTTH"].notna()) & (gdf["NODO_HFC"].notna())).sum()
        sin_cob = gdf["COBERTURA"].eq("No").sum()
        
        # Porcentajes
        total_analizados = len(gdf)
        
        return {
            "total_registros_excel": total_registros,
            "registros_filtrados": registros_filtrados,
            "registros_analizados": total_analizados,
            "con_ftth": int(con_ftth),
            "con_hfc": int(con_hfc),
            "con_ambas": int(con_ambas),
            "sin_cobertura": int(sin_cob),
            "porcentaje_cobertura": round((total_analizados - sin_cob) / total_analizados * 100, 2) if total_analizados > 0 else 0,
            "nodos_ftth_unicos": gdf["NODO_FTTH"].nunique(),
            "nodos_hfc_unicos": gdf["NODO_HFC"].nunique()
        }
    
    def cleanup(self):
        """Limpia recursos"""
        if self.parser:
            self.parser.cleanup()