import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .p-card {
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3); padding: 25px; border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1); margin-bottom: 20px;
    }
    .welcome-text { color: #1e3a8a; font-weight: 900; font-size: 35px; margin-bottom: 5px; }
    .badge-paid { background-color: #d4edda; color: #155724; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 11px; }
    .badge-debt { background-color: #f8d7da; color: #721c24; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 11px; }
    .badge-late { background-color: #343a40; color: #ffffff; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 11px; }
    .state-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0080ff 100%);
        color: white; padding: 12px 20px; border-radius: 12px; margin: 20px 0; font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
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
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.title("🚀 IACargo.io")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ ADMINISTRADOR ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    # A. REGISTRO (Con métodos de pago)
    with t_reg:
        st.subheader("Registro Inicial de Paquete")
        with st.form("reg_form_fix", clear_on_submit=True):
            c1, c2 = st.columns(2)
            f_id = c1.text_input("ID Tracking / Guía")
            f_cli = c1.text_input("Nombre del Cliente")
            f_cor = c1.text_input("Correo del Cliente")
            f_pes = c2.number_input("Peso Inicial Mensajero (Kg)", min_value=0.0, step=0.1)
            f_metodo = c2.selectbox("Método de Pago:", ["Pago Inmediato", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar Paquete"):
                if
