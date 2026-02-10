import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL EVOLUCIONADA ---
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

    /* Estilo para Título y Slogan Cursivo Profesional (ESTÁTICO) */
    .fuente-cursiva {
        font-family: 'Dancing Script', cursive !important;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        line-height: 1.1;
        text-align: center;
    }

    /* Contenedores Glassmorphism (Efecto cristal) */
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
        color: white !important;
    }

    /* Títulos con Degradado */
    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px; margin-bottom: 10px; 
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

    /* Botones con Estilo Moderno */
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

    /* Botón Eliminar (Rojo Profundo) */
    .btn-eliminar button { 
        background: linear-gradient(90deg, #ef4444, #b91c1c) !important; 
    }

    /* Campos de Entrada */
    input, select, textarea {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE DATOS (MANTENIDA) ---
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
    else: st.markdown('<h1 class="fuente-cursiva" style="font-size: 35px; text-align: left;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.markdown('<p class="fuente-cursiva" style="font-size: 16px; text-align: left; color: #a78bfa;">“Trabajamos para conectarte en todas partes del mundo”</p>', unsafe_allow_html=True)
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ DE ADMINISTRADOR ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro de Entrada")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, 
                        "Monto_USD": f_pes*PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                        "Pago": "PENDIENTE", "Modalidad": f_mod, "Abonado": 0.0, "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success(f"✅ Guía {f_id} registrada.")

    with t_val:
        st.subheader("Báscula de Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para Pesar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Cliente: {paq['Cliente']} | Peso Reportado: {paq['Peso_Mensajero']} Kg")
            peso_real = st.number_input("Peso Real en Báscula (Kg)", min_value=0.0, value=float(paq['Peso_Mensajero']), step=0.1)
            if st.button("⚖️ Validar Peso"):
                paq['Peso_Almacen'] = peso_real
                paq['Validado'] = True
                paq['Monto_USD'] = peso_real * PRECIO_POR_KG
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("✅ Peso validado."); st.rerun()
        else: st.info("Sin pendientes.")

    with t_cob:
        st.subheader("Gestión de Cobros")
        if st.session_state.inventario:
            pendientes_pago = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
            for p in pendientes_pago:
                with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']}"):
                    total = p['Monto_USD']
                    abonado = p.get('Abonado', 0.0)
                    resta = total - abonado
                    st.write(f"Modalidad: **{p.get('Modalidad')}** | Resta: **${resta:.2f}**")
                    monto_abono = st.number_input(f"Abonar a {p['ID_Barra']}", min_value=0.0, max_value=float(resta), key=f"c_{p['ID_Barra']}")
                    if st.button(f"Registrar Pago", key=f"b_{p['ID_Barra']}"):
                        p['Abonado'] = abonado + monto_abono
                        if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader("Logística de Envío")
        if st.session_state.inventario:
            sel_e = st.selectbox("ID de Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "
