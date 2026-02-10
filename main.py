import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    .logo-animado { font-style: italic !important; font-family: 'Georgia', serif; background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; animation: pulse 2.5s infinite; font-weight: 800; margin-bottom: 5px; }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }
    .stTabs, .stForm, [data-testid="stExpander"], .p-card { background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px !important; padding: 20px; margin-bottom: 15px; color: white !important; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 10px; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    .badge-paid { background: linear-gradient(90deg, #059669, #10b981); color: white !important; padding: 4px 10px; border-radius: 8px; font-weight: bold; font-size: 12px; display: inline-block; }
    .badge-pending { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 4px 10px; border-radius: 8px; font-weight: bold; font-size: 12px; display: inline-block; }
    .state-header { background: rgba(255, 255, 255, 0.1); border-left: 5px solid #3b82f6; color: #60a5fa !important; padding: 12px; border-radius: 8px; margin: 20px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .stButton>button { border-radius: 12px !important; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important; color: white !important; border: none !important; font-weight: 600 !important; transition: all 0.3s ease !important; width: 100% !important; }
    .btn-eliminar button { background: linear-gradient(90deg, #ef4444, #b91c1c) !important; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    .warning-box { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; padding: 10px; border-radius: 10px; color: #f87171; font-weight: bold; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"

TARIFA_AEREO_KG = 5.0
TARIFA_MARITIMO_FT3 = 18.0

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

def calcular_monto(valor, tipo):
    return valor * (TARIFA_AEREO_KG if tipo == "Aéreo" else TARIFA_MARITIMO_FT3)

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
        if st.button("Cerrar Sesión", use_container_width=True): 
            st.session_state.usuario_identificado = None; st.rerun()
    else:
        rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ ADMIN ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    # (Las funciones de administración se mantienen íntegras como en la versión anterior)
    with t_reg:
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo")
            f_tra = st.selectbox("Traslado", ["Aéreo", "Marítimo"])
            f_val_ini = st.number_input("Medida Inicial", min_value=0.0)
            f_mod = st.selectbox("Modalidad", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar"):
                if f_id and f_cli:
                    nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_val_ini, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": calcular_monto(f_val_ini, f_tra), "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                    st.session_state.inventario.append(nuevo); guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Registrado.")

    with t_val:
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("Validar Guía:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            v_real = st.number_input("Medida Real", value=float(paq['Peso_Mensajero']))
            if abs(v_real - paq['Peso_Mensajero']) > 0.01: st.markdown('<div class="warning-box">⚠️ Alerta de variación detectada.</div>', unsafe_allow_html=True)
            if st.button("⚖️ Validar"):
                paq.update({'Peso_Almacen': v_real, 'Validado': True, 'Monto_USD': calcular_monto(v_real, paq['Tipo_Traslado'])})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
        else: st.info("Sin pendientes.")

    with t_cob:
        for p in [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']:
            with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']}"):
                resta = p['Monto_USD'] - p.get('Abonado', 0.0)
                m_abono = st.number_input(f"Abonar a {p['ID_Barra']}", 0.0, float(resta), key=f"c_{p['ID_Barra']}")
                if st.button("Pagar", key=f"b_{p['ID_Barra']}"):
                    p['Abonado'] += m_abono
                    if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_est:
        if st.session_state.inventario:
            sel_e = st.selectbox("ID Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Estatus:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_e: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader("Auditoría")
        df_aud = pd.DataFrame(st.session_state.inventario)
        st.dataframe(df_aud, use_container_width=True)

    with t_res:
        st.subheader("📊 Resumen")
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            df_res['Deuda'] = df_res['Monto_USD'] - df_res['Abonado']
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Caja Real", f"${df_res['Abonado'].sum():.2f}")
            m2.metric("Por Cobrar", f"${df_res['Deuda'].sum():.2f}")
            for est in ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"]:
                df_f = df_res[df_res['Estado'] == est]
                st.markdown(f'<div class="state-header"> {est} </div>', unsafe_allow_html=True)
                st.table(df_f[['ID_Barra', 'Cliente', 'Pago', 'Deuda']])

# --- 5. PANEL DEL CLIENTE (RESTITUCIÓN DE BUSCADOR E ICONOS) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo')).lower() == str(u.get('correo')).lower()]
    
    if not mis_p:
        st.info("Aún no tienes paquetes registrados en nuestro sistema.")
    else:
        # --- REINCORPORACIÓN: BUSCADOR POR ID ---
        st.write("---")
        busqueda_id = st.text_input("🔍 Localizar paquete por ID / Tracking:", placeholder="Ej: ABC12345")
        
        # Filtrado lógico
        if busqueda_id:
            mis_p = [p for p in mis_p if busqueda_id.lower() in str(p['ID_Barra']).lower()]
        
        st.subheader("📋 Estado de mis Envíos")
        
        if not mis_p:
            st.warning("No se encontraron paquetes con ese ID.")
        
        for p in mis_p:
            total = p['Monto_USD']
            abonado = p.get('Abonado', 0.0)
            deuda = total - abonado
            pago_status = "PAGADO" if p.get('Pago') == "PAGADO" else "PENDIENTE"
            class_badge = "badge-paid" if pago_status == "PAGADO" else "badge-pending"
            icon = "✈️" if p.get('Tipo_Traslado') == "Aéreo" else "🚢"
            
            with st.container():
                st.markdown(f"""
                    <div class="p-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.2em; font-weight: bold; color: #60a5fa;">{icon} #{p['ID_Barra']}</span>
                            <span class="{class_badge}">{pago_status}</span>
                        </div>
                        <div style="margin: 15px 0; font-size: 0.95em;">
                            <b>📍 Estatus Logístico:</b> {p['Estado']}<br>
                            <b>💰 Monto Total:</b> ${total:.2f} | <b>Deuda Actual:</b> <span style="color:#f87171;">${deuda:.2f}</span>
                        </div>
                """, unsafe_allow_html=True)
                
                # Barra de avance de pago
                if total > 0:
                    progreso = min(abonado / total, 1.0)
                    st.progress(progreso)
                    st.caption(f"Progreso del pago: {progreso*100:.1f}%")
                
                st.markdown("</div>", unsafe_allow_html=True)

# --- 6. ACCESO ---
else:
    st.write("<br><br>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown('<div style="text-align: center;"><div class="logo-animado" style="font-size: 70px;">IACargo.io</div></div>', unsafe_allow_html=True)
        t1, t2 = st.tabs(["Ingresar", "Registro"])
        with t1:
            le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
            if st.button("Entrar", use_container_width=True):
                if le == "admin" and lp == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                u = next((u for u in st.session_state.usuarios if u['correo'] == le.lower().strip() and u['password'] == hash_password(lp)), None)
                if u: st.session_state.usuario_identificado = u; st.rerun()
                else: st.error("Credenciales inválidas.")
        with t2:
            with st.form("signup"):
                n = st.text_input("Nombre"); e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                if st.form_submit_button("Crear Cuenta"):
                    st.session_state.usuarios.append({"nombre": n, "correo": e.lower().strip(), "password": hash_password(p), "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Registrado."); st.rerun()
