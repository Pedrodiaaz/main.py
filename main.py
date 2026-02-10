import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL EVOLUCIONADA ---
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
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
        color: white !important;
    }

    /* ESTILO PARA LOS ENCABEZADOS DE ESTADO EN RESUMEN */
    .header-resumen {
        background: linear-gradient(90deg, #2563eb, #1e40af);
        color: white !important;
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.1em;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-left: 6px solid #60a5fa;
    }

    .resumen-row {
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding: 15px;
        border-bottom: 2px solid #cbd5e1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 5px;
        border-radius: 4px;
    }
    .resumen-id { font-weight: 800; color: #2563eb; width: 150px; }
    .resumen-cliente { flex-grow: 1; font-weight: 500; font-size: 1.1em; }
    .resumen-data { font-weight: 700; color: #475569; text-align: right; }
    
    .welcome-text { 
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800; font-size: 38px; margin-bottom: 10px; 
    }

    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }

    /* --- OPTIMIZACIÓN BOTÓN DE REGISTRO (FORMULARIO) --- */
    /* Forzamos el color azul estático y letras blancas sin cambios al pasar el mouse */
    div[data-testid="stForm"] button {
        background-color: #2563eb !important;
        background-image: none !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid #60a5fa !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        transition: none !important;
        width: 100% !important;
    }

    div[data-testid="stForm"] button:hover, 
    div[data-testid="stForm"] button:active, 
    div[data-testid="stForm"] button:focus {
        background-color: #2563eb !important;
        color: white !important;
        border: 1px solid #60a5fa !important;
    }

    /* Estilo para botones fuera de formularios (opcional, para mantener coherencia) */
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        width: 100% !important;
    }

    .btn-eliminar button { background: linear-gradient(90deg, #ef4444, #b91c1c) !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_POR_KG = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            df = pd.read_csv(archivo)
            if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            return df.to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.markdown('<h1 class="logo-animado" style="font-size: 30px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None; st.rerun()
    else: rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
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
            f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"]) 
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            # ESTE ES EL BOTÓN QUE AHORA ES AZUL ESTÁTICO
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, 
                        "Monto_USD": f_pes*PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                        "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, 
                        "Abonado": 0.0, "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success(f"✅ Guía {f_id} registrada.")

    with t_val:
        st.subheader("Báscula de Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para Pesar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Cliente: {paq['Cliente']} | Peso Reportado: {paq['Peso_Mensajero']} Kg")
            peso_real = st.number_input("Peso Real en Báscula (Kg)", min_value=0.0, value=float(paq['Peso_Mensajero']), step=0.1)
            if st.button("⚖️ Validar Peso"):
                paq['Peso_Almacen'] = peso_real; paq['Validado'] = True; paq['Monto_USD'] = peso_real * PRECIO_POR_KG
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("✅ Peso validado."); st.rerun()
        else: st.info("Sin pendientes.")

    # ... El resto del código de Cobros, Estados, Auditoría y Resumen se mantiene igual ...
    # (Lo omito aquí para no saturar, pero el estilo del botón ya quedó blindado en el CSS arriba)
    
    with t_res:
        st.subheader("📊 Resumen General de Operaciones")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            busq_res = st.text_input("🔍 Buscar caja por código:", key="res_search")
            if busq_res: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
            
            cant_almacen = len(df_res[df_res['Estado'] == "RECIBIDO ALMACEN PRINCIPAL"])
            cant_transito = len(df_res[df_res['Estado'] == "EN TRANSITO"])
            cant_entregados = len(df_res[df_res['Estado'] == "ENTREGADO"])
            
            m1, m2, m3 = st.columns(3)
            m1.metric("📦 En Almacén", f"{cant_almacen} Paq.")
            m2.metric("✈️ En Tránsito", f"{cant_transito} Paq.")
            m3.metric("✅ Entregados", f"{cant_entregados} Paq.")
            
            st.write("---")
            
            estados_mapeo = {
                "RECIBIDO ALMACEN PRINCIPAL": "📦 Mercancía en Almacén",
                "EN TRANSITO": "✈️ Mercancía en Tránsito",
                "ENTREGADO": "✅ Mercancía Entregada"
            }

            for est_key, est_label in estados_mapeo.items():
                df_f = df_res[df_res['Estado'] == est_key].copy()
                st.markdown(f'<div class="header-resumen">{est_label} ({len(df_f)})</div>', unsafe_allow_html=True)
                
                if not df_f.empty:
                    for _, row in df_f.iterrows():
                        icon = "✈️" if row.get('Tipo_Traslado') == "Aéreo" else "🚢"
                        st.markdown(f"""
                            <div class="resumen-row">
                                <div class="resumen-id">{icon} {row['ID_Barra']}</div>
                                <div class="resumen-cliente">{row['Cliente']}</div>
                                <div class="resumen-data">
                                    {row['Peso_Almacen']:.1f} Kg | {row['Pago']} | ${row['Abonado']:.2f}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("No hay registros en este estado.")
# (Faltaría cerrar los bloques if/else del código original)
