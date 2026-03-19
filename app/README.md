# 📡 Claro Cobertura Pro

Sistema profesional de análisis geoespacial para cobertura de redes HFC y FTTH de Claro Colombia.

## 🚀 Características

- *Análisis Masivo*: Procesamiento de archivos Excel con órdenes de trabajo
- *Visualización Interactiva*: Mapas con polígonos de cobertura FTTH y HFC
- *Consultas en Tiempo Real*:
  - Por nombre de nodo
  - Por coordenadas GPS
  - Por dirección colombiana (geocodificación)
- *Reportes Profesionales*: Exportación a Excel y CSV
- *Interfaz Corporativa*: Branding Claro (Rojo #DA291C)

## 📋 Requisitos

- Python 3.11.7
- Dependencias en requirements.txt

## 🛠️ Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/tuusuario/claro-cobertura-pro.git
cd claro-cobertura-pro

# Crear entorno virtual
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
streamlit run app/main.py