"""
Configuración global del sistema Claro Cobertura Pro
"""
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KMZ_DIR = os.path.join(DATA_DIR, "kmz")
TEMP_DIR = os.path.join(DATA_DIR, "temp")

# Crear directorios si no existen
os.makedirs(KMZ_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Branding Claro
BRAND = {
    "name": "Claro",
    "full_name": "Claro Colombia",
    "primary_color": "#DA291C",      # Rojo Claro
    "secondary_color": "#FFFFFF",     # Blanco
    "accent_color": "#F2F2F2",        # Gris claro
    "text_color": "#333333",
    "success_color": "#28A745",
    "warning_color": "#FFC107",
    "danger_color": "#DC3545"
}

# Tolerancia geoespacial
TOLERANCIA_METROS = 50
TOLERANCIA_GRADOS = TOLERANCIA_METROS / 111000  # ~0.00045 grados

# Actividades válidas
ACTIVIDADES_VALIDAS = ["Instalaciones", "INSTALACIONES FTTH", "TRASLADO FTTH", "Traslados"]

# Columnas esperadas en el Excel
COLUMNAS_REQUERIDAS = [
    "Tipo de Actividad",
    "Estado", 
    "Coordenada X",
    "Coordenada Y"
]

# Configuración de geocoding
GEOCODING_CONFIG = {
    "user_agent": "ClaroCoberturaPro/1.0",
    "timeout": 10,
    "min_delay_seconds": 1
}