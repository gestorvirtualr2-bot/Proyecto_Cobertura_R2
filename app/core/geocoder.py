"""
Servicio de geocodificación para direcciones colombianas
"""
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.point import Point
import time
from app.config import GEOCODING_CONFIG

class ColombiaGeocoder:
    """Geocodificador especializado para Colombia"""
    
    def __init__(self):
        self.geolocator = Nominatim(
            user_agent=GEOCODING_CONFIG["user_agent"],
            timeout=GEOCODING_CONFIG["timeout"]
        )
        self.last_query_time = 0
    
    def _rate_limit(self):
        """Control de rate limiting"""
        min_delay = GEOCODING_CONFIG["min_delay_seconds"]
        elapsed = time.time() - self.last_query_time
        if elapsed < min_delay:
            time.sleep(min_delay - elapsed)
        self.last_query_time = time.time()
    
    def geocode_address(self, address):
        """
        Geocodifica una dirección colombiana
        
        Formatos soportados:
        - Calle 80 # 22-10
        - Carrera 80 # 22-10  
        - AV 72 # 54A-24
        - etc.
        """
        self._rate_limit()
        
        # Normalizar dirección para Colombia
        address_clean = self._normalize_address(address)
        
        try:
            location = self.geolocator.geocode(
                address_clean,
                country_codes="CO",  # Limitar a Colombia
                exactly_one=True,
                language="es"
            )
            
            if location:
                return {
                    "success": True,
                    "address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "raw": location.raw
                }
            else:
                return {
                    "success": False,
                    "error": "Dirección no encontrada"
                }
                
        except GeocoderTimedOut:
            return {
                "success": False,
                "error": "Tiempo de espera agotado"
            }
        except GeocoderServiceError as e:
            return {
                "success": False,
                "error": f"Error del servicio: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error inesperado: {str(e)}"
            }
    
    def reverse_geocode(self, lat, lon):
        """Geocodificación inversa"""
        self._rate_limit()
        
        try:
            location = self.geolocator.reverse(
                Point(lat, lon),
                language="es",
                exactly_one=True
            )
            
            if location:
                return {
                    "success": True,
                    "address": location.address,
                    "latitude": lat,
                    "longitude": lon
                }
            else:
                return {
                    "success": False,
                    "error": "Coordenadas no encontradas"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _normalize_address(self, address):
        """
        Normaliza direcciones colombianas para mejor búsqueda
        """
        address = address.upper().strip()
        
        # Reemplazar abreviaturas comunes
        replacements = {
            "CARRERA": "CARRERA",
            "CRA": "CARRERA",
            "CR": "CARRERA",
            "CALLE": "CALLE",
            "CL": "CALLE",
            "AVENIDA": "AVENIDA",
            "AV": "AVENIDA",
            "AV.": "AVENIDA",
            "TRANSVERSAL": "TRANSVERSAL",
            "TV": "TRANSVERSAL",
            "DIAGONAL": "DIAGONAL",
            "DG": "DIAGONAL",
            "#": " # ",
            "-": " - "
        }
        
        for old, new in replacements.items():
            address = address.replace(old, new)
        
        # Agregar Colombia si no está
        if "COLOMBIA" not in address:
            address += ", COLOMBIA"
            
        return address
    
    def search_node_polygon(self, node_name, coverage_gdf):
        """
        Busca un nodo por nombre y retorna su geometría
        """
        if coverage_gdf is None or coverage_gdf.empty:
            return None
            
        # Buscar coincidencias exactas o parciales
        mask = coverage_gdf['nombre'].str.upper().str.contains(
            node_name.upper(), 
            na=False
        )
        
        matches = coverage_gdf[mask]
        
        if matches.empty:
            return None
            
        # Retornar el primero (podría retornar lista si hay múltiples)
        return {
            "nombre": matches.iloc[0]['nombre'],
            "geometry": matches.iloc[0].geometry,
            "tipo": matches.iloc[0].get('tipo', 'Desconocido'),
            "bounds": matches.iloc[0].geometry.bounds
        }