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
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    [data-testid="stSidebar"] { display: none; }
    
    .logout-container {
        position: fixed; top: 20px; right: 20px; z-index: 1000;
        display: flex; align-items: center; gap: 15px;
        background: rgba(255, 255, 255, 0.1); padding: 8px 15px;
        border-radius: 30px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Estilo Campana */
    .nav-icons { display: flex; align-items: center; gap: 20px; margin-right: 10px; }
    .bell-icon { font-size: 1.5rem; cursor: pointer; position: relative; }
    .bell-badge {
        position: absolute; top: -5px; right: -5px;
        background: #ef4444; color: white; border-radius: 50%;
        padding: 2px 6px; font-size: 0.7rem; font-weight: bold;
    }

    .logo-animado {
        font-style: italic !important; font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        display: inline-block; animation: pulse 2.5s infinite;
        font-weight: 800; margin-bottom: 5px;
    }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }

    .stTabs, .stForm, [data-testid="stExpander"], .p-card, .notif-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important; padding: 20px; margin-bottom: 15px; color: white !important;
    }
    
    .notif-card { padding: 10px 15px; border-radius: 12px !important; margin-bottom: 8px; border-left: 4px solid #60a5fa; }

    div[data-baseweb="input"] { border-radius: 10px !important; background-color: #f8fafc !important; }
    div[data-baseweb="input"] input { color: #1e293b !important; }
    .stButton button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: white !important; border-radius: 12px !important; font-weight: 700 !important;
        text-transform: uppercase !important; border: none !important; transition: all 0.3s ease !important;
    }
    .badge-paid { background: #10b981; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.8em; font-weight: bold; }
    .badge-debt { background: #f87171; color: white; padding: 4px 10px; border-radius: 10px; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
ARCHIVO_NOTIF = "notificaciones.csv"
PRECIO_POR_UNIDAD = 5.0

def hash_password(password): return hashlib.sha256(str.encode(password)).hexdigest()
def generar_id_unico(): return f"IAC-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try: return pd.read_csv(archivo).to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

# Inicializar estados
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'notificaciones' not in st.session_state: st.session_state.notificaciones = cargar_datos(ARCHIVO_NOTIF)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'id_actual' not in st.session_state: st.session_state.id_actual = generar_id_unico()
if 'landing_vista' not in st.session_state: st.session_state.landing_vista = True

def agregar_notificacion(correo, id_guia, nuevo_estado):
    notif = {
        "correo": correo.lower().strip(),
        "mensaje": f"📦 La guía **{id_guia}** ha cambiado a: **{nuevo_estado}**",
        "fecha": datetime.now().strftime("%d/%m %H:%M"),
        "leida": False
    }
    st.session_state.notificaciones.append(notif)
    guardar_datos(st.session_state.notificaciones, ARCHIVO_NOTIF)

# --- 3. FUNCIONES DE DASHBOARD ---
def render_admin_dashboard():
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_est:
        st.subheader("✈️ Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "RECIBIDO EN ALMACEN DE DESTINO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e:
                        if p["Estado"] != n_st:
                            p["Estado"] = n_st
                            agregar_notificacion(p["Correo"], p["ID_Barra"], n_st)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("Estado actualizado y cliente notificado."); st.rerun()

    # (Resto de pestañas admin se mantienen igual...)
    with t_reg:
        st.subheader("Registro de Entrada")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"], key="admin_reg_tra")
        label_din = "Pies Cúbicos" if f_tra == "Marítimo" else "Peso (Kg / Lbs)"
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input(label_din, min_value=0.0, step=0.1)
            if st.form_submit_button("Registrar en Sistema"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes * PRECIO_POR_UNIDAD, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": "Pago Completo", "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.session_state.id_actual = generar_id_unico()
                st.rerun()

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    
    # Lógica de Notificaciones
    mis_notif = [n for n in st.session_state.notificaciones if n['correo'] == u['correo'].lower().strip()]
    no_leidas = [n for n in mis_notif if not n.get('leida')]

    col_title, col_notif = st.columns([0.85, 0.15])
    with col_title:
        st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    with col_notif:
        # Campana de notificaciones
        with st.popover(f"🔔 {len(no_leidas) if no_leidas else ''}"):
            st.markdown("### Novedades")
            if not mis_notif:
                st.write("No tienes notificaciones aún.")
            else:
                for n in reversed(mis_notif):
                    st.markdown(f"""
                        <div class="notif-card">
                            <small style="color:#94a3b8;">{n['fecha']}</small><br>
                            <span style="font-size:0.9em;">{n['mensaje']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                if st.button("Marcar todas como leídas"):
                    for n in mis_notif: n['leida'] = True
                    guardar_datos(st.session_state.notificaciones, ARCHIVO_NOTIF)
                    st.rerun()

    # Búsqueda y Cards de paquetes (se mantiene igual)
    busq_cli = st.text_input("🔍 Buscar mis paquetes por código de barra:")
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    if busq_cli: mis_p = [p for p in mis_p if busq_cli.lower() in str(p.get('ID_Barra')).lower()]
    
    if not mis_p: st.info("No tienes envíos registrados.")
    else:
        c1, c2 = st.columns(2)
        for i, p in enumerate(mis_p):
            with (c1 if i % 2 == 0 else c2):
                st.markdown(f"""
                    <div class="p-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="color:#60a5fa; font-weight:800; font-size:1.2em;">📦 #{p['ID_Barra']}</span>
                            <span class="badge-debt">{p.get('Estado')}</span>
                        </div>
                        <hr style="opacity:0.1; margin:10px 0;">
                        <small>Estatus Actualización: Tiempo real</small>
                    </div>
                """, unsafe_allow_html=True)

# --- 4. LÓGICA DE NAVEGACIÓN ---
if st.session_state.usuario_identificado is None:
    if st.session_state.landing_vista:
        st.markdown("<br><br><br><div style='text-align:center;'><h1 class='logo-animado' style='font-size:80px;'>IACargo.io</h1><br>", unsafe_allow_html=True)
        if st.button("🚀 INGRESAR AL SISTEMA", use_container_width=True):
            st.session_state.landing_vista = False; st.rerun()
    else:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center;"><div class="logo-animado" style="font-size:60px;">IACargo.io</div></div>', unsafe_allow_html=True)
            with st.form("login_form"):
                le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
                if st.form_submit_button("Entrar"):
                    if le == "admin" and lp == "admin123":
                        st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin", "correo": "admin@iacargo.io"}; st.rerun()
                    u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                    if u: st.session_state.usuario_identificado = u; st.rerun()
                    else: st.error("Error")
            if st.button("⬅️ Volver"): st.session_state.landing_vista = True; st.rerun()
else:
    st.markdown(f'<div class="logout-container"><span style="color:#60a5fa; font-weight:bold;">Socio: {st.session_state.usuario_identificado["nombre"]}</span></div>', unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN 🔒"):
        st.session_state.usuario_identificado = None
        st.session_state.landing_vista = True; st.rerun()

    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
