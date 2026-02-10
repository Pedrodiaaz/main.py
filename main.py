import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Importar fuente cursiva profesional */
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&display=swap');

    /* Fondo General Tecnológico */
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }

    /* Estilo para Título y Slogan Cursivo Profesional (ESTÁTICO Y LIMPIO) */
    .fuente-cursiva {
        font-family: 'Dancing Script', cursive !important;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        line-height: 1.1;
        text-align: center;
    }

    /* Contenedores Glassmorphism */
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
        color: white !important;
    }

    /* Forzar visibilidad de textos */
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }

    /* Badges de Estado */
    .badge-paid { 
        background: linear-gradient(90deg, #059669, #10b981); 
        color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; 
    }
    .badge-debt { 
        background: linear-gradient(90deg, #dc2626, #f87171); 
        color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; 
    }

    /* Cabeceras de Logística */
    .state-header {
        background: rgba(255, 255, 255, 0.1);
        border-left: 5px solid #3b82f6;
        color: #60a5fa !important; padding: 12px; border-radius: 8px; margin: 20px 0; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1px;
    }

    /* Botones */
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }

    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÓGICA DE DATOS (FUNCIONALIDAD GARANTIZADA) ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_KG = 5.0

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns:
                df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo):
    pd.DataFrame(datos).to_csv(archivo, index=False)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown('<h1 class="fuente-cursiva" style="font-size: 35px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.markdown('<p class="fuente-cursiva" style="font-size: 1
