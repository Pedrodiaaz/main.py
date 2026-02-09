import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .p-card {
        background: white;
        padding: 22px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 6px solid #0080FF;
        margin-bottom: 18px;
    }
    .welcome-text {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 28px;
        margin-bottom: 15px;
    }
    .state-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #0080FF 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin-top: 25px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTOR DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
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
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.markdown(f"**Socio Activo:**\n{st.session_state.usuario_identificado.get('nombre', 'Admin')}")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Sección:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ ADMINISTRADOR ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_res = tabs

    with t_reg:
        with st.form("reg_form"):
            f_id = st.text_input("ID Tracking")
            f_cli = st.text_input("Cliente")
            f_cor = st.text_input("Correo")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0)
            if st.form_submit_button("Registrar"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                         "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False,
                         "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO",
                         "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("Registrado.")

    with t_val:
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia = st.selectbox("Validar Guía:", [p["ID_Barra"] for p in pendientes])
            peso_real = st.number_input("Peso Báscula (Kg)")
            if st.button("Validar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == guia:
                        p.update({"Peso_Almacen": peso_real, "Validado": True, "Monto_USD": peso_real * PRECIO_POR_KG})
                        if abs(peso_real - p['Peso_Mensajero']) > 0.1: st.error("🚨 DIFERENCIA DE PESO")
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.rerun()

    with t_cob:
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            hoy = datetime.now()
            df['Estatus'] = df.apply(lambda r: 'PAGADO' if r['Pago'] == 'PAGADO' else ('ATRASADO' if (hoy - pd.to_datetime(r['Fecha_Registro'])).days > 15 else 'PENDIENTE'), axis=1)
            st.dataframe(df[['ID_Barra', 'Cliente', 'Monto_USD', 'Estatus']])

    with t_res:
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            st.metric("Total Ingresos (Pagados)", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")

# --- 5. PANEL DEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    mis_p = [p for p in st.session_state.inventario if p.get('Correo', '').lower() == u['correo'].lower()]
    
    if mis_p:
        df_c = pd.DataFrame(mis_p)
        hoy = datetime.now()
        df_c['Estatus_Pago'] = df_c.apply(lambda r: 'PAGADO' if r['Pago'] == 'PAGADO' else ('ATRASADO' if (hoy - pd.to_datetime(r['Fecha_Registro'])).days > 15 else 'PENDIENTE'), axis=1)
        
        st.metric("Deuda Total", f"${df_c[df_c['Estatus_Pago'] != 'PAGADO']['Monto_USD'].sum():.2f}")
        
        for _, p in df_c.iterrows():
            color = "#28a745" if p['Estatus_Pago'] == 'PAGADO' else ("#dc3545" if p['Estatus_Pago'] == 'ATRASADO' else "#FFCC00")
            st.markdown(f"""
                <div class="p-card" style="border-left: 6px solid {color};">
                    <h3 style="margin:0;">📦 Guía: {p['ID_Barra']}</h3>
                    <p>Estado: <b>{p['Estado']}</b> | Pago: <b>{p['Estatus_Pago']}</b></p>
                    <p>Monto: ${p['Monto_USD']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No tienes paquetes registrados.")

# --- 6. LOGIN ---
else:
    if rol_vista == "🔑 Portal Clientes":
        e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
        if st.button("Entrar"):
            user = next((u for u in st.session_state.usuarios if u['correo'] == e.lower().strip() and u['password'] == hash_password(p)), None)
            if user: st.session_state.usuario_identificado = user; st.rerun()
    else:
        ad_u = st.text_input("Admin"); ad_p = st.text_input("Pass", type="password")
        if st.button("Acceso Admin"):
            if ad_u == "admin" and ad_p == "admin123":
                st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
