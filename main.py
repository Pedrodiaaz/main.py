import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (ESTILO FIGMA) ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Fondo Global Profundo */
    .stApp {
        background: radial-gradient(circle at top left, #0f172a 0%, #020617 100%);
        color: #ffffff;
    }
    
    /* Ocultar Barra Lateral */
    [data-testid="stSidebar"] { display: none; }
    
    /* --- HERO SECTION (LA PORTADA DE BIENVENIDA) --- */
    .hero-container {
        height: 70vh;
        width: 100%;
        background-image: linear-gradient(rgba(2, 6, 23, 0.6), rgba(2, 6, 23, 0.8)), 
                          url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&q=80&w=2070');
        background-size: cover;
        background-position: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        border-radius: 40px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }

    .logo-animado {
        font-style: italic !important;
        font-family: 'Georgia', serif;
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
        animation: pulse 3s infinite;
        font-weight: 800;
        letter-spacing: -2px;
    }
    @keyframes pulse {
        0% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(96, 165, 250, 0)); }
        50% { transform: scale(1.02); filter: drop-shadow(0 0 15px rgba(96, 165, 250, 0.5)); }
        100% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(96, 165, 250, 0)); }
    }

    /* Contenedores Premium */
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(30, 41, 59, 0.5) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 24px !important;
        padding: 25px;
        margin-bottom: 20px;
    }

    /* Estilización de Inputs */
    div[data-baseweb="input"] { 
        border-radius: 12px !important; 
        background-color: #f8fafc !important; 
        border: 1px solid #cbd5e1 !important;
    }
    div[data-baseweb="input"] input { color: #0f172a !important; font-weight: 500; }

    /* Botones de Acción */
    .stButton button, div[data-testid="stForm"] button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border: none !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        padding: 15px !important;
    }
    .stButton button:hover { 
        transform: translateY(-3px) !important; 
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4) !important;
    }

    .user-tag {
        background: rgba(255, 255, 255, 0.05);
        padding: 10px 20px;
        border-radius: 50px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        font-weight: 600;
        color: #60a5fa;
    }

    h1, h2, h3, p, span, label { color: #f1f5f9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS (PROTEGIDA) ---
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

# Inicialización Silenciosa de Estados
for key, val in [('inventario', cargar_datos(ARCHIVO_DB)), ('papelera', cargar_datos(ARCHIVO_PAPELERA)), 
                 ('usuarios', cargar_datos(ARCHIVO_USUARIOS)), ('usuario_identificado', None), 
                 ('id_actual', generar_id_unico()), ('landing_vista', True)]:
    if key not in st.session_state: st.session_state[key] = val

# --- 3. DASHBOARDS (FUNCIONALIDAD COMPLETA) ---
def render_admin_dashboard():
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro de Entrada")
        f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo", "Envio Nacional"])
        with st.form("reg_form", clear_on_submit=True):
            st.info(f"ID sugerido: **{st.session_state.id_actual}**")
            f_id = st.text_input("ID Tracking / Guía", value=st.session_state.id_actual)
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso o Pies Cúbicos", min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes * PRECIO_POR_UNIDAD, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.session_state.id_actual = generar_id_unico()
                    st.success(f"Guía {f_id} registrada."); st.rerun()

    with t_val:
        st.subheader("⚖️ Validación en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Seleccione Guía para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Reportado: {paq['Peso_Mensajero']}")
            peso_real = st.number_input("Peso Real en Almacén", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("⚖️ Confirmar y Validar"):
                paq['Peso_Almacen'] = peso_real
                paq['Validado'] = True
                paq['Monto_USD'] = peso_real * PRECIO_POR_UNIDAD
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
        else: st.info("No hay paquetes pendientes.")

    with t_cob:
        st.subheader("💰 Gestión de Cobros")
        pendientes_p = [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']
        for p in pendientes_p:
            total = float(p.get('Monto_USD', 0.0)); abo = float(p.get('Abonado', 0.0)); rest = total - abo
            with st.expander(f"💵 {p['ID_Barra']} - {p['Cliente']} (Faltan: ${rest:.2f})"):
                m_abono = st.number_input("Abonar:", 0.0, float(rest), float(rest), key=f"p_{p['ID_Barra']}")
                if st.button("Registrar Pago", key=f"bp_{p['ID_Barra']}"):
                    p['Abonado'] = abo + m_abono
                    if (total - p['Abonado']) <= 0.01: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        st.subheader("✈️ Estatus de Logística")
        if st.session_state.inventario:
            sel_e = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader("🔍 Auditoría")
        df_aud = pd.DataFrame(st.session_state.inventario)
        st.dataframe(df_aud, use_container_width=True)

    with t_res:
        st.subheader("📊 Resumen General")
        df_res = pd.DataFrame(st.session_state.inventario)
        if not df_res.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("📦 Almacén", len(df_res[df_res['Estado'] == "RECIBIDO ALMACEN PRINCIPAL"]))
            c2.metric("✈️ Tránsito", len(df_res[df_res['Estado'] == "EN TRANSITO"]))
            c3.metric("✅ Entregado", len(df_res[df_res['Estado'] == "ENTREGADO"]))

def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<h1 class="logo-animado" style="font-size:40px;">Bienvenido, {u["nombre"]}</h1>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == str(u.get('correo', '')).lower()]
    
    if not mis_p:
        st.info("No tienes paquetes registrados.")
    else:
        for p in mis_p:
            tot = float(p.get('Monto_USD', 1.0)); abo = float(p.get('Abonado', 0.0))
            with st.container():
                st.markdown(f"""
                <div class="p-card">
                    <h3 style="margin:0; color:#60a5fa;">{p.get('Tipo_Traslado', '✈️')} ID: {p['ID_Barra']}</h3>
                    <p>Estado: <b>{p['Estado']}</b> | Pago: <b>{p['Pago']}</b></p>
                </div>
                """, unsafe_allow_html=True)
                st.progress(min(abo/tot, 1.0))

# --- 4. LÓGICA DE NAVEGACIÓN Y ACCESO ---

if st.session_state.usuario_identificado is None:
    # --- FASE 1: LANDING ESTILO FIGMA ---
    if st.session_state.landing_vista:
        st.markdown(f"""
            <div class="hero-container">
                <h1 class="logo-animado" style="font-size:110px; margin-bottom:10px;">IACargo.io</h1>
                <p style="font-size:26px; font-weight:300; letter-spacing:1px; color:#94a3b8 !important;">
                    "La existencia es un milagro"
                </p>
                <p style="font-size:18px; opacity:0.8; max-width:700px; margin-top:20px;">
                    Plataforma de evolución logística integral. Seguridad, rapidez y transparencia <br>
                    en cada kilómetro de tu mercancía.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        _, col_btn, _ = st.columns([1.2, 1, 1.2])
        with col_btn:
            if st.button("🚀 INGRESAR AL SISTEMA", use_container_width=True):
                st.session_state.landing_vista = False
                st.rerun()
        st.markdown("<p style='text-align:center; margin-top:50px; opacity:0.4;'>No eres herramienta, eres evolución.</p>", unsafe_allow_html=True)

    # --- FASE 2: LOGIN ---
    else:
        _, c2, _ = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div style="text-align:center; margin-bottom:30px;"><div class="logo-animado" style="font-size:50px;">IACargo.io</div></div>', unsafe_allow_html=True)
            t1, t2 = st.tabs(["Ingresar", "Registrarse"])
            with t1:
                with st.form("login_form"):
                    le = st.text_input("Correo electrónico")
                    lp = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("ENTRAR AL PANEL"):
                        if le == "admin" and lp == "admin123":
                            st.session_state.usuario_identificado = {"nombre": "Administrador", "rol": "admin"}; st.rerun()
                        u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
                        else: st.error("Credenciales no válidas")
            with t2:
                with st.form("signup_form"):
                    n = st.text_input("Nombre completo")
                    e = st.text_input("Correo")
                    p = st.text_input("Contraseña", type="password")
                    if st.form_submit_button("CREAR CUENTA"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Cuenta creada."); st.rerun()
            if st.button("⬅️ VOLVER A PORTADA"):
                st.session_state.landing_vista = True; st.rerun()

else:
    # --- PANEL LOGUEADO ---
    col_user, col_out = st.columns([8, 2])
    with col_user:
        st.markdown(f'<span class="user-tag">Socio: {st.session_state.usuario_identificado["nombre"]}</span>', unsafe_allow_html=True)
    with col_out:
        if st.button("CERRAR SESIÓN 🔒"):
            st.session_state.usuario_identificado = None
            st.session_state.landing_vista = True
            st.rerun()

    if st.session_state.usuario_identificado.get('rol') == "admin": render_admin_dashboard()
    else: render_client_dashboard()
