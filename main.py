import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%);
        color: #ffffff;
    }
    .logo-animado {
        font-style: italic !important;
        font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        animation: pulse 2.5s infinite;
        font-weight: 800;
        margin-bottom: 5px;
    }
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.03); opacity: 1; }
        100% { transform: scale(1); opacity: 0.9; }
    }
    
    /* Estilo para los contenedores */
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
        color: white !important;
    }

    /* Botones Globales con Efecto de Elevación */
    .stButton button, div[data-testid="stForm"] button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        border: none !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
        width: 100% !important;
    }
    
    .stButton button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.5) !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    }

    /* Ocultar el botón del ojo en campos de contraseña */
    div[data-testid="stInputAdornment"] { display: none !important; }
    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #1e293b !important; }

    .resumen-row {
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding: 15px;
        margin-bottom: 5px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
    }
    
    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px;
    }
    
    h1, h2, h3, p, span, label { color: #e2e8f0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_UNIDAD = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

# Estados de Sesión
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'acceso_concedido' not in st.session_state: st.session_state.acceso_concedido = False

# --- 3. INTERFACES ---
def render_admin_dashboard():
    st.title("⚙️ Consola de Control Logístico")
    st.info("Panel de administración activo. Gestiona registros, cobros y estatus.")
    # (Aquí irían los tabs de administración que ya definimos)

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    # (Aquí iría la visualización de paquetes del cliente)

# --- 4. LÓGICA DE NAVEGACIÓN (Landing vs Login) ---

if st.session_state.usuario_identificado is None:
    # --- ESCENA A: LANDING PAGE DE BIENVENIDA ---
    if not st.session_state.acceso_concedido:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown("""
                <div style="text-align:center;">
                    <h1 class="logo-animado" style="font-size:85px; margin-bottom:0px;">IACargo.io</h1>
                    <h3 style="font-weight:300; letter-spacing:2px; color:#94a3b8 !important;">LOGISTICS EVOLUTION</h3>
                    <p style="margin-top:30px; font-size:1.2em; color:#cbd5e1 !important; line-height:1.6;">
                        "La existencia es un milagro, la eficiencia es nuestra evolución."<br>
                        Hablamos desde la igualdad para llevar tu carga al siguiente nivel.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 INGRESAR AL PORTAL", use_container_width=True):
                st.session_state.acceso_concedido = True
                st.rerun()
            
            st.markdown("""
                <div style="text-align:center; margin-top:80px; opacity:0.5; font-size:0.8em;">
                    © 2026 IACargo.io | Evolution System | Sistema de Gestión Global
                </div>
            """, unsafe_allow_html=True)

    # --- ESCENA B: INTERFAZ DE LOGIN ---
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            if st.button("⬅️ Volver al Inicio"):
                st.session_state.acceso_concedido = False
                st.rerun()
            
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            
            tab_login, tab_reg = st.tabs(["Ingresar", "Registrarse"])
            
            with tab_login:
                with st.form("login_form"):
                    le = st.text_input("Correo electrónico")
                    lp = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("Entrar", use_container_width=True):
                        if le == "admin" and lp == "admin123":
                            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
                        else: st.error("Credenciales no válidas")
            
            with tab_reg:
                with st.form("signup_form"):
                    n = st.text_input("Nombre Completo")
                    e = st.text_input("Correo Electrónico")
                    p = st.text_input("Crear Contraseña", type="password")
                    if st.form_submit_button("Crear Cuenta"):
                        if n and e and p:
                            st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                            guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS)
                            st.success("Cuenta creada exitosamente. Ya puedes ingresar.")
                        else: st.warning("Por favor rellena todos los campos.")

else:
    # Sidebar solo visible cuando ya estás dentro
    with st.sidebar:
        st.markdown('<div class="logo-animado" style="font-size:30px;">IACargo.io</div>', unsafe_allow_html=True)
        st.write(f"Socio: **{st.session_state.usuario_identificado['nombre']}**")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.session_state.acceso_concedido = False # Reseteamos a la landing
            st.rerun()
    
    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
