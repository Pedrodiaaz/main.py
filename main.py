import streamlit as st
import pandas as pd
import os
import hashlib
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
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px;
        margin-bottom: 15px;
    }
    .state-header {
        background: rgba(59, 130, 246, 0.1);
        border-left: 5px solid #60a5fa;
        padding: 10px 15px;
        border-radius: 5px;
        margin: 15px 0;
        font-weight: bold;
        color: #60a5fa !important;
    }
    .stButton>button {
        border-radius: 12px !important;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .btn-eliminar button { 
        background: linear-gradient(90deg, #ef4444, #b91c1c) !important; 
    }
    input, select, textarea {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
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
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.markdown('<h1 class="logo-animado" style="font-size: 30px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre')}")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        st.caption("“La existencia es un milagro”")
    st.write("---")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ ADMIN ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0)
            f_tra = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"])
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli:
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes*PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success(f"Guía {f_id} registrada.")

    with t_val:
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Guía para Pesar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            peso_real = st.number_input("Peso Real (Kg)", min_value=0.0, value=float(paq['Peso_Mensajero']))
            if st.button("⚖️ Validar Peso"):
                paq.update({'Peso_Almacen': peso_real, 'Validado': True, 'Monto_USD': peso_real * PRECIO_POR_KG})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_cob:
        for p in [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']:
            with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']}"):
                resta = p['Monto_USD'] - p.get('Abonado', 0.0)
                monto = st.number_input(f"Abonar a {p['ID_Barra']}", 0.0, float(resta), key=f"c_{p['ID_Barra']}")
                if st.button("Registrar Pago", key=f"b_{p['ID_Barra']}"):
                    p['Abonado'] = p.get('Abonado', 0.0) + monto
                    if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        if st.session_state.inventario:
            sel_e = st.selectbox("ID de Guía:", [p["ID_Barra"] for p in st.session_state.inventario], key="est_sel")
            n_st = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        busq = st.text_input("🔍 Buscar Guía para editar:")
        df_aud = pd.DataFrame(st.session_state.inventario)
        if not df_aud.empty:
            guia_ed = st.selectbox("Seleccione ID:", df_aud['ID_Barra'].tolist())
            paq_ed = next(p for p in st.session_state.inventario if p["ID_Barra"] == guia_ed)
            c1, c2 = st.columns(2)
            with c1: new_cli = st.text_input("Nombre Cliente", value=paq_ed['Cliente'])
            with c2: new_pes = st.number_input("Peso (Kg)", value=float(paq_ed['Peso_Almacen']))
            if st.button("💾 Guardar Cambios"):
                paq_ed.update({'Cliente': new_cli, 'Peso_Almacen': new_pes, 'Monto_USD': new_pes*PRECIO_POR_KG})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Actualizado"); st.rerun()

    with t_res:
        st.subheader("📊 Resumen de Mercancía")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            busq_res = st.text_input("🔍 Buscar caja por código:", key="res_search")
            if busq_res:
                df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Kg Totales", f"{df_res['Peso_Almacen'].sum():.1f}")
            m2.metric("Paquetes", len(df_res))
            m3.metric("Caja (Abonos)", f"${df_res['Abonado'].sum():.2f}")

            for e_int, e_vis in {"RECIBIDO ALMACEN PRINCIPAL": "📦 EN ALMACÉN", "EN TRANSITO": "✈️ EN TRÁNSITO", "ENTREGADO": "✅ ENTREGADO"}.items():
                df_f = df_res[df_res['Estado'] == e_int]
                st.markdown(f'<div class="state-header">{e_vis} ({len(df_f)})</div>', unsafe_allow_html=True)
                if not df_f.empty: st.table(df_f[['ID_Barra', 'Cliente', 'Peso_Almacen', 'Pago', 'Abonado']])
        else: st.info("Inventario vacío.")

# --- 5. LOGIN ---
else:
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="logo-animado" style="font-size: 60px; text-align: center; display:block;">IACargo.io</div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ingresar", "Registro"])
        with t1:
            le = st.text_input("Correo", key="l_e")
            lp = st.text_input("Clave", type="password", key="l_p")
            if st.button("Iniciar Sesión"):
                if le == "admin" and lp == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if u: st.session_state.usuario_identificado = u; st.rerun()
                else: st.error("Error de acceso")
        with t2:
            with st.form("signup"):
                n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Crear Cuenta"):
                    if n and e and p:
                        st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Creada."); st.rerun()
