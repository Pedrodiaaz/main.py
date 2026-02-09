import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL (FONDO AZUL CORPORATIVO) ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* FONDO CORPORATIVO CON DISEÑO DE CONECTORES */
    .stApp {
        background: linear-gradient(135deg, #001f3f 0%, #004080 50%, #001f3f 100%);
        background-attachment: fixed;
        background-size: cover;
    }

    /* CAPA DE TEXTURA (Líneas de Conexión sutiles) */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px);
        background-size: 30px 30px;
        z-index: -1;
    }

    /* TARJETAS CONTENEDORAS (Para que el texto sea legible sobre el azul) */
    div.stBlock {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    /* Estilo de Pestañas */
    .stTabs [data-baseweb="tab-list"] { background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #0080FF !important; border-radius: 8px; }

    /* Títulos en Blanco para resaltar sobre el fondo */
    h1, h2, h3, .stMarkdown p { color: #ffffff; }
    
    /* Reajuste de tarjetas de métricas */
    .metric-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2); border-top: 5px solid #0080FF;
        text-align: center; color: #333 !important;
    }
    .metric-card h3, .metric-card p { color: #333 !important; }

    /* Estilo de las Cajas de Resumen en Admin */
    .summary-box {
        background: white; color: #333; padding: 20px;
        border-radius: 15px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
PRECIO_POR_KG = 5.0

# --- 2. MOTOR DE PERSISTENCIA ---
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

if 'inventario' not in st.session_state: 
    st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuario_identificado' not in st.session_state: 
    st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.write(f"Socio: **{st.session_state.usuario_identificado['correo']}**")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Sección:", ["🔑 Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. PANEL ADMINISTRATIVO ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Consola de Evolución Logística")
    
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN PESO", "✈️ ESTADOS", "💰 COBROS", "🔍 AUDITORÍA", "📊 RESUMEN"])
    t_reg, t_val, t_est, t_cob, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Entrada de Mercancía")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("Guía / Tracking")
            f_cli = st.text_input("Cliente")
            f_cor = st.text_input("Correo")
            f_pes = st.number_input("Peso Inicial (Kg)", min_value=0.0)
            if st.form_submit_button("Registrar"):
                st.session_state.inventario.append({
                    "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower(), "Peso_Origen": f_pes,
                    "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                    "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()
                })
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("✅ Guía registrada.")

    with t_val:
        st.subheader("Validación de Peso")
        if st.session_state.inventario:
            sel = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            paq = next((p for p in st.session_state.inventario if p["ID_Barra"] == sel), None)
            if paq:
                new_w = st.number_input("Peso Validado (Kg)", value=float(paq['Peso_Origen']))
                if st.button("Confirmar Peso"):
                    paq['Peso_Origen'] = new_w
                    paq['Monto_USD'] = new_w * PRECIO_POR_KG
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success("✅ Peso actualizado.")

    with t_est:
        st.subheader("Fases de Traslado")
        if st.session_state.inventario:
            sel = st.selectbox("Actualizar Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            new_e = st.selectbox("Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel: p["Estado"] = new_e
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.rerun()

    with t_cob:
        st.subheader("Cobros")
        pendientes = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
        for idx, p in enumerate(pendientes):
            c_a, c_b = st.columns([3, 1])
            c_a.info(f"{p['ID_Barra']} - ${p['Monto_USD']}")
            if c_b.button("Cobrar", key=f"c_{idx}"):
                p["Pago"] = "PAGADO"
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.rerun()

    with t_aud:
        st.subheader("Auditoría")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 Descargar CSV", df.to_csv(index=False).encode('utf-8'), "IACargo.csv")

    with t_res:
        st.subheader("Dashboard")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-card">Kg Totales<br><h3>{df["Peso_Origen"].sum():.1f}</h3></div>', unsafe_allow_html=True)
            with m2: st.markdown(f'<div class="metric-card">Guías<br><h3>{len(df)}</h3></div>', unsafe_allow_html=True)
            with m3: st.markdown(f'<div class="metric-card">Pagado<br><h3>${df[df["Pago"]=="PAGADO"]["Monto_USD"].sum():.2f}</h3></div>', unsafe_allow_html=True)

# --- 5. PANEL CLIENTE ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Mi Carga")
    u_mail = st.session_state.usuario_identificado['correo'].lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    for p in mis_p:
        with st.container():
            st.markdown(f'<div class="summary-box" style="margin-bottom:20px;"><h3>Guía: {p["ID_Barra"]}</h3><p>Estado: {p["Estado"]}</p></div>', unsafe_allow_html=True)

# --- 6. LOGIN ---
else:
    st.subheader("Acceso IACargo.io")
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if u == "admin" and p == "admin123":
            st.session_state.usuario_identificado = {"correo": "ADMIN", "rol": "admin"}
        else:
            st.session_state.usuario_identificado = {"correo": u.lower(), "rol": "cliente"}
        st.rerun()
