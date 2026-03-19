"""
Estilos CSS personalizados para branding Claro
"""
import streamlit as st

def apply_claro_styles():
    """Aplica los estilos corporativos de Claro"""
    
    st.markdown("""
        <style>
        /* Fondo principal */
        .stApp {
            background-color: #FFFFFF;
        }
        
        /* Header personalizado */
        .claro-header {
            background: linear-gradient(135deg, #DA291C 0%, #B91C1C 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .claro-header h1 {
            color: white !important;
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
        }
        
        .claro-header p {
            color: rgba(255,255,255,0.9) !important;
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
        }
        
        /* Botones estilo Claro */
        .stButton > button {
            background-color: #DA291C !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            width: 100%;
        }
        
        .stButton > button:hover {
            background-color: #B91C1C !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(218, 41, 28, 0.4) !important;
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Botón secundario */
        .stButton > button[kind="secondary"] {
            background-color: #6C757D !important;
        }
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            border-radius: 8px !important;
            border: 2px solid #E0E0E0 !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #DA291C !important;
            box-shadow: 0 0 0 3px rgba(218, 41, 28, 0.1) !important;
        }
        
        /* File uploader */
        .stFileUploader {
            border: 2px dashed #DA291C !important;
            border-radius: 10px !important;
            padding: 2rem !important;
            background-color: #FFF5F5 !important;
        }
        
        .stFileUploader:hover {
            background-color: #FFEBEB !important;
        }
        
        /* Métricas */
        .stMetric {
            background: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #DA291C;
        }
        
        .stMetric label {
            color: #666 !important;
            font-weight: 600 !important;
        }
        
        .stMetric .css-1xarl3l {
            color: #DA291C !important;
            font-weight: 700 !important;
        }
        
        /* Tablas */
        .stDataFrame {
            border-radius: 10px !important;
            overflow: hidden !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #F8F9FA !important;
        }
        
        .css-1d391kg .stRadio > label {
            font-weight: 600 !important;
            color: #333 !important;
        }
        
        /* Cards */
        .claro-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            border: 1px solid #E0E0E0;
            margin-bottom: 1rem;
        }
        
        .claro-card h3 {
            color: #DA291C !important;
            margin-top: 0 !important;
        }
        
        /* Status badges */
        .badge-success {
            background-color: #28A745;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        .badge-warning {
            background-color: #FFC107;
            color: #333;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        .badge-danger {
            background-color: #DC3545;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        /* Map container */
        .map-container {
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: 2px solid #DA291C;
        }
        
        /* Progress bar */
        .stProgress > div > div > div {
            background-color: #DA291C !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #F8F9FA !important;
            border-radius: 8px !important;
            border: 1px solid #E0E0E0 !important;
        }
        
        /* Footer */
        .claro-footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.875rem;
            border-top: 1px solid #E0E0E0;
            margin-top: 3rem;
        }
        
        /* Animaciones */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #DA291C;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #B91C1C;
        }
        </style>
    """, unsafe_allow_html=True)

def show_header(title="Sistema de Análisis de Cobertura", subtitle="Claro Colombia"):
    """Muestra el header corporativo"""
    st.markdown(f"""
        <div class="claro-header animate-fade-in">
            <h1>📡 {title}</h1>
            <p>{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)

def show_footer():
    """Muestra el footer"""
    st.markdown("""
        <div class="claro-footer">
            <p>© 2024 Claro Colombia. Todos los derechos reservados.</p>
            <p>Sistema de Análisis Geoespacial - Versión 1.0 PRO</p>
        </div>
    """, unsafe_allow_html=True)