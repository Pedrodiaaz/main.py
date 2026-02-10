import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (NIVEL EVOLUCIÓN) ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    .logo-animado { font-style: italic !important; font-family: 'Georgia', serif; background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; animation: pulse 2.5s infinite; font-weight: 800; margin-bottom: 5px; }
    @keyframes pulse { 0% { transform: scale(1); opacity: 0.9; } 50% { transform: scale(1.03); opacity: 1; } 100% { transform: scale(1); opacity: 0.9; } }
    .stTabs, .stForm, [data-testid="stExpander"], .p-card { background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px !important; padding: 20px; margin-bottom: 15px; color: white !important; }
    .welcome-text { background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 38px; margin-bottom: 10px; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #e2e8f0 !important; }
    .badge-paid { background: linear-gradient(90deg, #059669, #10b981); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .badge-pending { background: linear-gradient(90deg, #dc2626, #f87171); color: white !important; padding: 5px 12px; border-radius: 12px; font-weight: bold; font-size: 11px; }
    .state-header { background: rgba(255, 255, 255, 0.15); border-left: 5px solid #3b82f6; color: #60a5fa !important; padding: 15px; border-radius: 10px; margin: 25px 0 10px 0; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
    .stButton>button { border-radius: 12px !important; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important; color: white !important; border: none !important; font-weight: 600 !important; transition: all 0.3s ease !important; width: 100% !important; }
    .warning-box { background: rgba(239, 68, 68, 0.2); border: 1px solid #ef4444; padding: 15px; border-radius: 10px; color: #f87171; font-weight: bold; margin-bottom: 15px; }
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid rgba(255, 255, 255, 0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE ARCHIVOS Y DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
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
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.markdown('<h1 class="logo-animado" style="font-size: 32px;">IACargo.io</h1>', unsafe_allow_html=True)
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Sesión: {st.session_state.usuario_identificado.get('nombre')}")
        if st.button("Cerrar Sesión"): 
            st.session_state.usuario_identificado = None; st.rerun()
    else:
        rol_vista = st.radio("Sección:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ ADMINISTRADOR (RESTURADA) ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Sistema Maestro de Logística")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "✈️ ESTADOS", "💰 COBROS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_est, t_cob, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Ingreso de Mercancía")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("Código de Tracking / Guía")
            f_cli = st.text_input("Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_tra = st.selectbox("Tipo de Envío", ["Aéreo", "Marítimo"])
            f_peso_ini = st.number_input("Peso/Medida Inicial (Mensajero)", min_value=0.0)
            f_mod = st.selectbox("Modalidad de Pago", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar Paquete"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_peso_ini, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": calcular_monto(f_peso_ini, f_tra), "Estado": "EN ALMACÉN", "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": f_tra, "Abonado": 0.0, "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo); guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("✅ Registrado con éxito.")

    with t_val:
        st.subheader("⚖️ Verificación de Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia_v = st.selectbox("ID a Validar:", [p["ID_Barra"] for p in pendientes])
            paq = next(p for p in pendientes if p["ID_Barra"] == guia_v)
            st.info(f"Declarado: {paq['Peso_Mensajero']} | Traslado: {paq['Tipo_Traslado']}")
            v_real = st.number_input("Peso/Medida Real en Báscula", value=float(paq['Peso_Mensajero']))
            
            diferencia = abs(v_real - paq['Peso_Mensajero'])
            if diferencia > 0.1:
                st.markdown(f'<div class="warning-box">⚠️ ALARMA: Variación de {diferencia:.2f} detectada. Verifique integridad.</div>', unsafe_allow_html=True)
            
            if st.button("Validar y Procesar"):
                paq.update({'Peso_Almacen': v_real, 'Validado': True, 'Monto_USD': calcular_monto(v_real, paq['Tipo_Traslado'])})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("✅ Validación completada."); st.rerun()
        else: st.info("No hay mercancía pendiente por validar.")

    with t_est:
        st.subheader("✈️ Control de Tránsito")
        if st.session_state.inventario:
            guia_st = st.selectbox("Seleccione Guía para mover:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Cambiar Estatus a:", ["EN ALMACÉN", "EN TRÁNSITO", "ENTREGADO"])
            if st.button("Actualizar Posición"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == guia_st: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Estatus actualizado."); st.rerun()

    with t_res:
        st.subheader("📊 Resumen Maestro por Estado")
        busq_res = st.text_input("🔍 Buscar caja por código:", key="search_res")
        df_res = pd.DataFrame(st.session_state.inventario)
        if busq_res: df_res = df_res[df_res['ID_Barra'].astype(str).str.contains(busq_res, case=False)]
        
        for estado_f in ["EN ALMACÉN", "EN TRÁNSITO", "ENTREGADO"]:
            df_sec = df_res[df_res['Estado'] == estado_f]
            st.markdown(f'<div class="state-header">{estado_f} ({len(df_sec)})</div>', unsafe_allow_html=True)
            if not df_sec.empty:
                st.table(df_sec[['ID_Barra', 'Cliente', 'Tipo_Traslado', 'Peso_Almacen', 'Pago']])

    with t_aud:
        st.subheader("Edición y Auditoría")
        df_aud = pd.DataFrame(st.session_state.inventario)
        st.dataframe(df_aud, use_container_width=True)

    with t_cob:
        for p in [p for p in st.session_state.inventario if p['Pago'] == 'PENDIENTE']:
            with st.expander(f"💰 {p['ID_Barra']} - {p['Cliente']}"):
                falta = p['Monto_USD'] - p.get('Abonado', 0.0)
                st.write(f"Deuda: ${falta:.2f}")
                abono = st.number_input(f"Abonar a {p['ID_Barra']}", 0.0, float(falta), key=f"ab_{p['ID_Barra']}")
                if st.button("Confirmar Pago", key=f"bt_{p['ID_Barra']}"):
                    p['Abonado'] += abono
                    if p['Abonado'] >= p['Monto_USD']: p['Pago'] = 'PAGADO'
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Hola, {u["nombre"]}</div>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo')).lower() == str(u.get('correo')).lower()]
    busq_cli = st.text_input("🔍 Buscar mi guía:")
    if busq_cli: mis_p = [p for p in mis_p if busq_cli.lower() in str(p['ID_Barra']).lower()]
    
    for p in mis_p:
        st_pago = p.get('Pago', 'PENDIENTE')
        badge = "badge-paid" if st_pago == "PAGADO" else "badge-pending"
        with st.container():
            st.markdown(f'<div class="p-card"><span class="{badge}">{st_pago}</span><br><b>Guía: #{p["ID_Barra"]}</b><br>📍 Ubicación: {p["Estado"]}<br>Falta pagar: ${(p["Monto_USD"]-p["Abonado"]):.2f}</div>', unsafe_allow_html=True)
            if p['Monto_USD'] > 0: st.progress(min(p['Abonado']/p['Monto_USD'], 1.0))

# --- 6. PANTALLA DE ACCESO (RESTURADA TOTAL) ---
else:
    st.write("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center;"><div class="logo-animado" style="font-size: 85px;">IACargo.io</div><p style="color: #a78bfa !important; font-size: 1.2em;">Evolución y Logística Sin Límites</p></div>', unsafe_allow_html=True)
        t_ac, t_re = st.tabs(["🔐 Ingresar", "📝 Registrarse"])
        with t_ac:
            ce = st.text_input("Correo electrónico")
            cp = st.text_input("Contraseña", type="password")
            if st.button("Entrar al Sistema", use_container_width=True):
                if ce == "admin" and cp == "admin123":
                    st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                u = next((u for u in st.session_state.usuarios if u['correo'] == ce.lower().strip() and u['password'] == hash_password(cp)), None)
                if u: st.session_state.usuario_identificado = u; st.rerun()
                else: st.error("Credenciales incorrectas.")
        with t_re:
            with st.form("registro_user"):
                rn = st.text_input("Nombre Completo")
                re = st.text_input("Correo Electrónico")
                rp = st.text_input("Crear Contraseña", type="password")
                if st.form_submit_button("Crear Cuenta"):
                    if rn and re and rp:
                        st.session_state.usuarios.append({"nombre": rn, "correo": re.lower().strip(), "password": hash_password(rp), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("¡Cuenta creada! Inicia sesión."); st.rerun()
