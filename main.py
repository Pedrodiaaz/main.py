import streamlit as st
import pandas as pd
import os
import smtplib
import random
import hashlib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution", layout="wide", page_icon="🚀")

# Estilo UI/UX Profesional
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .p-card { background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 6px solid #0080FF; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .status-text { font-weight: bold; color: #0080FF; }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

# CONFIGURACIÓN DE CORREO (Asegúrate de configurar tu Contraseña de Aplicación)
EMAIL_EMISOR = "tu_correo@gmail.com" 
PASS_EMISOR = "tu_contraseña_de_aplicacion" 

# --- 2. MOTOR DE COMUNICACIÓN Y SEGURIDAD ---

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

def enviar_correo(correo_destino, asunto, mensaje_html):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = f"IACargo.io Support <{EMAIL_EMISOR}>"
        msg['To'] = correo_destino
        msg.attach(MIMEText(mensaje_html, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_EMISOR, PASS_EMISOR)
        server.sendmail(EMAIL_EMISOR, correo_destino, msg.as_string())
        server.quit()
        return True
    except: return False

# Inicialización de Sesión
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None
if 'otp_generado' not in st.session_state: st.session_state.otp_generado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Sesión: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Acceso:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")

# --- 4. PANEL DE USUARIO (TARJETAS + LÍNEA DE TIEMPO) ---

if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Mi Centro de Seguimiento")
    u_mail = st.session_state.usuario_identificado['correo'].lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if mis_p:
        for p in mis_p:
            with st.container():
                st.markdown(f"""
                <div class="p-card">
                    <h3>Paquete: {p['ID_Barra']}</h3>
                    <p>Estatus Actual: <span class="status-text">{p['Estado']}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                est = p['Estado']
                prog, p1, p2, p3 = 0, "⚪", "⚪", "⚪"
                if "RECIBIDO" in est: prog, p1 = 33, "🔵"
                elif "TRANSITO" in est: prog, p1, p2 = 66, "🔵", "🔵"
                elif "ENTREGADO" in est: prog, p1, p2, p3 = 100, "🔵", "🔵", "🔵"
                
                st.progress(prog)
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"{p1} **RECIBIDO**")
                c2.markdown(f"{p2} **EN TRÁNSITO**")
                c3.markdown(f"{p3} **ENTREGADO**")
                st.write(f"**Detalles:** Monto a pagar: ${p['Monto_USD']} | Pago: {p['Pago']}")
                st.write("---")
    else:
        st.info("No hay envíos registrados vinculados a este correo.")

# --- 5. PANEL DE ADMINISTRACIÓN ---

elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Consola de Comando Admin")
    t_res, t_reg, t_pes, t_cob, t_aud = st.tabs(["📊 Resumen", "📝 Registro", "⚖️ Estados", "💰 Cobros", "🔍 Auditoría"])

    with t_res:
        if st.session_state.inventario:
            df_res = pd.DataFrame(st.session_state.inventario)
            df_res['Fecha_Registro'] = pd.to_datetime(df_res['Fecha_Registro'])
            periodo = st.selectbox("Periodo:", ["Semanal", "Mensual", "Anual"])
            dias_map = {"Semanal": 7, "Mensual": 30, "Anual": 365}
            df_f = df_res[df_res['Fecha_Registro'] >= (datetime.now() - timedelta(days=dias_map[periodo]))]
            m1, m2, m3 = st.columns(3)
            m1.metric("Clientes", len(df_f['Correo'].unique()))
            m2.metric("Kilos", f"{df_f['Peso_Origen'].sum():.1f}")
            m3.metric("Recaudado", f"${df_f[df_f['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")
            st.bar_chart(df_f.groupby(df_f['Fecha_Registro'].dt.date).agg({'Peso_Origen':'sum', 'Monto_USD':'sum'}))
        else: st.info("Sin datos.")

    with t_reg:
        with st.form("admin_reg_form", clear_on_submit=True):
            st.subheader("Entrada de Mercancía")
            c1, c2 = st.columns(2)
            id_i = c1.text_input("ID Tracking")
            cl_i = c1.text_input("Cliente")
            co_i = c2.text_input("Correo")
            pe_i = c2.number_input("Peso (Kg)", min_value=0.0)
            if st.form_submit_button("Finalizar Registro"):
                st.session_state.inventario.append({
                    "ID_Barra": id_i, "Cliente": cl_i, "Correo": co_i, "Peso_Origen": pe_i,
                    "Peso_Almacen": 0.0, "Monto_USD": pe_i*PRECIO_POR_KG, 
                    "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", 
                    "Fecha_Registro": datetime.now()
                })
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("✅ Registrado.")

    with t_pes:
        st.subheader("Estatus y Notificaciones")
        if st.session_state.inventario:
            sel_id = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            nuevo_est = st.selectbox("Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar y Notificar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_id:
                        p["Estado"] = nuevo_est
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        html = f"<h2>Actualización</h2><p>Paquete <b>{sel_id}</b> está: <b>{nuevo_est}</b>.</p>"
                        enviar_correo(p['Correo'], "Estatus IACargo.io", html)
                        st.success("✅ Estatus actualizado.")
                        st.rerun()

    with t_cob:
        sub1, sub2 = st.tabs(["❌ Por Cobrar", "✅ Pagados"])
        with sub1:
            deuda = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
            for idx, p in enumerate(deuda):
                c1, c2 = st.columns([3, 1])
                c1.warning(f"{p['ID_Barra']} | {p['Cliente']} | ${p['Monto_USD']}")
                if c2.button("Cobrar", key=f"p_btn_{idx}"):
                    p["Pago"] = "PAGADO"
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    enviar_correo(p['Correo'], "Pago Recibido", f"Confirmamos pago de {p['ID_Barra']}")
                    st.rerun()
        with sub2:
            pagados = [p for p in st.session_state.inventario if p["Pago"] == "PAGADO"]
            if pagados:
                df_p = pd.DataFrame(pagados)
                st.dataframe(df_p, use_container_width=True)
                st.download_button("📥 Excel", df_p.to_csv(index=False).encode('utf-8'), "Cierre.csv", "text/csv")

# --- 6. ACCESO CLIENTES ---
elif rol_vista == "🔑 Portal Clientes":
    st.title("Portal Clientes")
    l1, l2 = st.tabs(["Entrar", "Crear Cuenta"])
    with l2:
        if not st.session_state.otp_generado:
            cr = st.text_input("Correo")
            pr = st.text_input("Clave", type="password")
            if st.button("Enviar OTP"):
                otp = str(random.randint(100000, 999999))
                if enviar_correo(cr, "Código OTP", f"Tu código: {otp}"):
                    st.session_state.otp_generado = otp
                    st.session_state.datos_pre = {"correo": cr, "password": hash_password(pr)}
                    st.rerun()
        else:
            v_otp = st.text_input("Código")
            if st.button("Verificar"):
                if v_otp == st.session_state.otp_generado:
                    st.session_state.usuarios.append({**st.session_state.datos_pre, "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS)
                    st.session_state.otp_generado = None
                    st.success("✅ Cuenta activa.")
    with l1:
        lc, lp = st.text_input("Correo", key="lc"), st.text_input("Clave", type="password", key="lp")
        if st.button("Entrar"):
            u = next((u for u in st.session_state.usuarios if u['correo'] == lc and u['password'] == hash_password(lp)), None)
            if u: 
                st.session_state.usuario_identificado = u
                st.rerun()

elif rol_vista == "🔐 Administración":
    st.title("Acceso Staff")
    admin_u = st.text_input("Usuario")
    admin_p = st.text_input("Clave", type="password")
    if st.button("Acceder"):
        if admin_u == "admin" and admin_p == "admin123":
            st.session_state.usuario_identificado = {"correo": "ADMIN", "rol": "admin"}
            st.rerun()
