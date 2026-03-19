"""
Parser avanzado para archivos KMZ/KML de cobertura
"""
import zipfile
import xml.etree.ElementTree as ET
import os
import re
from shapely.geometry import Point, Polygon, MultiPolygon
import geopandas as gpd
from app.config import TEMP_DIR, TOLERANCIA_GRADOS

class KMZParser:
    """Parser especializado para archivos KMZ de Claro"""
    
    def __init__(self, kmz_path):
        self.kmz_path = kmz_path
        self.kml_path = None
        self.ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        self.temp_dir = os.path.join(TEMP_DIR, "kmz_extract")
        os.makedirs(self.temp_dir, exist_ok=True)
        
    def extract(self):
        """Extrae el KMZ y localiza el doc.kml"""
        with zipfile.ZipFile(self.kmz_path, 'r') as zip_ref:
            zip_ref.extractall(self.temp_dir)
        
        # Buscar doc.kml
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                if file == 'doc.kml':
                    self.kml_path = os.path.join(root, file)
                    return True
        return False
    
    def parse_coordinates(self, coords_text):
        """Parsea texto de coordenadas KML"""
        coords = []
        for punto in coords_text.split():
            partes = punto.split(',')
            if len(partes) >= 2:
                try:
                    lon = float(partes[0])
                    lat = float(partes[1])
                    coords.append((lon, lat))
                except:
                    continue
        return coords
    
    def extract_ftth_layers(self):
        """Extrae capas FTTH (Greenfield, Brownfield, Desconocido)"""
        ftth_propio = []
        
        try:
            import fiona
            capas = fiona.listlayers(self.kml_path)
            
            for capa in capas:
                capa_upper = capa.upper()
                if ("FTTH" in capa_upper and 
                    any(x in capa_upper for x in ["GREENFIELD", "BROWNFIELD", "DESCONOCIDO"])):
                    if "NO_APLICA" not in capa_upper:
                        gdf = gpd.read_file(self.kml_path, layer=capa)
                        if len(gdf) > 0:
                            if gdf.crs is None:
                                gdf.set_crs("EPSG:4326", inplace=True)
                            gdf = gdf.to_crs("EPSG:4326")
                            
                            # Buscar nombre
                            nombre_col = "NOMBRE_TK" if "NOMBRE_TK" in gdf.columns else "Name"
                            gdf["NOMBRE_TK"] = gdf[nombre_col].astype(str)
                            
                            for _, row in gdf.iterrows():
                                ftth_propio.append({
                                    "nombre": row["NOMBRE_TK"], 
                                    "geometry": row.geometry,
                                    "tipo": "FTTH Propio"
                                })
        except Exception as e:
            print(f"Error geopandas FTTH: {e}")
            
        return ftth_propio
    
    def extract_redes_neutras(self):
        """Extrae redes neutras manualmente del XML"""
        redes_neutras = []
        
        if not self.kml_path:
            return redes_neutras
            
        tree = ET.parse(self.kml_path)
        root = tree.getroot()
        
        # Buscar carpetas de redes neutras
        for folder in root.findall('.//kml:Folder', self.ns):
            name_elem = folder.find('kml:name', self.ns)
            if name_elem is None:
                continue
            
            folder_name = name_elem.text or ""
            folder_upper = folder_name.upper()
            
            if (any(x in folder_upper for x in ["COBERTURAS FTT", "RED NEUTRA", "NEUTRAS"]) and 
                "NO_APLICA" not in folder_upper):
                
                placemarks = folder.findall('.//kml:Placemark', self.ns)
                
                for placemark in placemarks:
                    # Nombre
                    pm_name_elem = placemark.find('kml:name', self.ns)
                    pm_name = pm_name_elem.text if pm_name_elem is not None else "SIN_NOMBRE"
                    
                    # Descripción (NOMBRE_TK)
                    desc_elem = placemark.find('kml:description', self.ns)
                    desc = desc_elem.text if desc_elem is not None else ""
                    
                    nombre_tk = pm_name
                    if desc and "NOMBRE_TK" in desc:
                        match = re.search(r'NOMBRE_TK[^>]*>([^<]+)', desc)
                        if match:
                            nombre_tk = match.group(1).strip()
                    
                    # Geometría
                    coords = None
                    
                    # Polygon simple
                    poly_elem = placemark.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', self.ns)
                    if poly_elem is not None and poly_elem.text:
                        coords = self.parse_coordinates(poly_elem.text)
                    
                    # MultiGeometry
                    if coords is None:
                        multigeom = placemark.find('.//kml:MultiGeometry', self.ns)
                        if multigeom is not None:
                            poly_elem = multigeom.find('.//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates', self.ns)
                            if poly_elem is not None and poly_elem.text:
                                coords = self.parse_coordinates(poly_elem.text)
                    
                    if coords and len(coords) >= 3:
                        try:
                            poly = Polygon(coords)
                            if poly.is_valid:
                                redes_neutras.append({
                                    "nombre": nombre_tk,
                                    "geometry": poly,
                                    "tipo": "Red Neutra"
                                })
                        except:
                            pass
        
        return redes_neutras
    
    def extract_hfc(self):
        """Extrae capa HFC"""
        capas_hfc = []
        
        try:
            import fiona
            capas = fiona.listlayers(self.kml_path)
            
            for capa in capas:
                if capa.upper() == "HFC":
                    gdf = gpd.read_file(self.kml_path, layer=capa)
                    if len(gdf) > 0:
                        if gdf.crs is None:
                            gdf.set_crs("EPSG:4326", inplace=True)
                        gdf = gdf.to_crs("EPSG:4326")
                        
                        nombre_col = "Name" if "Name" in gdf.columns else "NOMBRE"
                        gdf["NOMBRE_TK"] = gdf[nombre_col].astype(str)
                        
                        for _, row in gdf.iterrows():
                            capas_hfc.append({
                                "nombre": row["NOMBRE_TK"],
                                "geometry": row.geometry,
                                "tipo": "HFC"
                            })
        except Exception as e:
            print(f"Error HFC: {e}")
            
        return capas_hfc
    
    def get_all_coverages(self):
        """Obtiene todas las coberturas combinadas"""
        if not self.extract():
            return None, None
            
        ftth = self.extract_ftth_layers() + self.extract_redes_neutras()
        hfc = self.extract_hfc()
        
        gdf_ftth = gpd.GeoDataFrame(ftth, crs="EPSG:4326") if ftth else gpd.GeoDataFrame(
            columns=["nombre", "geometry", "tipo"], crs="EPSG:4326"
        )
        gdf_hfc = gpd.GeoDataFrame(hfc, crs="EPSG:4326") if hfc else gpd.GeoDataFrame(
            columns=["nombre", "geometry", "tipo"], crs="EPSG:4326"
        )
        
        return gdf_ftth, gdf_hfc
    
    def cleanup(self):
        """Limpia archivos temporales"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)