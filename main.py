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

# Estilos CSS para el Modelo de Interfaz solicitado
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .p-card { background-color: #ffffff; padding: 25px; border-radius: 15px; border-left: 6px solid #0080FF; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .status-active { background: #0080FF; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; }
    .status-inactive { background: #e9ecef; color: #adb5bd; padding: 10px; border-radius: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- CONSTANTES ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

# CONFIGURACIÓN DE CORREO (Debes usar tu contraseña de aplicación de Google)
EMAIL_EMISOR = "tu_correo@gmail.com" 
PASS_EMISOR = "tu_contraseña_de_aplicacion" 

# --- 2. MOTOR DE FUNCIONES INTEGRADO ---

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
    st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Usuario: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")

# --- 4. PANEL DE USUARIO (CON LÍNEA DE TIEMPO) ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Mis Envíos")
    u_mail = st.session_state.usuario_identificado['correo'].lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if mis_p:
        for p in mis_p:
            with st.container():
                st.markdown(f"""<div class="p-card"><h3>Guía: {p['ID_Barra']}</h3><p>Estado Actual: <b>{p['Estado']}</b></p></div>""", unsafe_allow_html=True)
                
                # LÓGICA DE LÍNEA DE TIEMPO VISUAL
                est = p['Estado']
                c1, c2, c3 = st.columns(3)
                
                # Paso 1
                if "RECIBIDO" in est or "TRANSITO" in est or "ENTREGADO" in est:
                    c1.markdown('<div class="status-active">1. RECIBIDO</div>', unsafe_allow_html=True)
                else: c1.markdown('<div class="status-inactive">1. RECIBIDO</div>', unsafe_allow_html=True)
                
                # Paso 2
                if "TRANSITO" in est or "ENTREGADO" in est:
                    c2.markdown('<div class="status-active">2. EN TRÁNSITO</div>', unsafe_allow_html=True)
                else: c2.markdown('<div class="status-inactive">2. EN TRÁNSITO</div>', unsafe_allow_html=True)
                
                # Paso 3
                if "ENTREGADO" in est:
                    c3.markdown('<div class="status-active">3. ENTREGADO</div>', unsafe_allow_html=True)
                else: c3.markdown('<div class="status-inactive">3. ENTREGADO</div>', unsafe_allow_html=True)
                
                st.write(f"**Detalles:** Pago: {p['Pago']} | Monto: ${p['Monto_USD']}")
                st.write("---")
    else:
        st.info("No hay paquetes vinculados a tu cuenta.")

# --- 5. PANEL DE ADMINISTRACIÓN (DASHBOARD COMPLETO) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Consola de Control Admin")
    t_res, t_reg, t_est, t_cob = st.tabs(["📊 RESUMEN", "📝 REGISTRO", "⚖️ ESTADOS", "💰 COBROS"])

    # RESUMEN (Gráficos y Métricas)
    with t_res:
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            col1, col2, col3 = st.columns(3)
            col1.metric("Kilos Totales", f"{df['Peso_Origen'].sum()} Kg")
            col2.metric("Guías Activas", len(df))
            col3.metric("Recaudación", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum()}")
            
            st.write("### Flujo de Paquetes por Fecha")
            df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            chart_data = df.groupby(df['Fecha_Registro'].dt.date).size()
            st.bar_chart(chart_data)
        else: st.info("Sin datos para analítica.")

    # REGISTRO
    with t_reg:
        with st.form("admin_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking")
            f_cli = st.text_input("Nombre Cliente")
            f_cor = st.text_input("Correo Cliente")
            f_pes = st.number_input("Peso (Kg)", min_value=0.0)
            if st.form_submit_button("Registrar Paquete"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor, "Peso_Origen": f_pes,
                         "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                         "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("✅ Guardado correctamente.")

    # ESTADOS (Notificaciones automáticas)
    with t_est:
        if st.session_state.inventario:
            sel = st.selectbox("Seleccionar Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            nuevo_e = st.selectbox("Cambiar Estado a:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar y Notificar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel:
                        p["Estado"] = nuevo_e
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        html = f"<h3>IACargo.io</h3><p>Tu paquete <b>{sel}</b> ha pasado a: <b>{nuevo_e}</b></p>"
                        enviar_correo(p['Correo'], "Actualización de Envío", html)
                        st.success("✅ Estado actualizado y cliente notificado.")
                        st.rerun()

    # COBROS (Exportación Excel)
    with t_cob:
        pendientes = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
        for idx, p in enumerate(pendientes):
            c1, c2 = st.columns([3, 1])
            c1.warning(f"{p['ID_Barra']} - {p['Cliente']} - ${p['Monto_USD']}")
            if c2.button("Confirmar Pago", key=f"p_{idx}"):
                p["Pago"] = "PAGADO"
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                enviar_correo(p['Correo'], "Pago Confirmado", f"Hemos recibido el pago de la guía {p['ID_Barra']}")
                st.rerun()
        
        st.write("---")
        df_all = pd.DataFrame(st.session_state.inventario)
        st.download_button("📥 Descargar Reporte Completo (Excel/CSV)", df_all.to_csv(index=False).encode('utf-8'), "IACargo_Reporte.csv", "text/csv")

# --- 6. ACCESO Y SEGURIDAD (OTP INTEGRADO) ---
elif rol_vista == "🔑 Portal Clientes":
    l1, l2 = st.tabs(["Entrar", "Crear Cuenta"])
    with l2:
        if not st.session_state.otp_generado:
            cr = st.text_input("Tu Correo")
            pr = st.text_input("Tu Clave", type="password")
            if st.button("Enviar Código de Verificación"):
                otp = str(random.randint(100000, 999999))
                if enviar_correo(cr, "Código OTP IACargo.io", f"Tu código es: {otp}"):
                    st.session_state.otp_generado = otp
                    st.session_state.datos_pre = {"correo": cr, "password": hash_password(pr)}
                    st.rerun()
        else:
            v_otp = st.text_input("Ingresa el código que recibiste")
            if st.button("Validar y Activar"):
                if v_otp == st.session_state.otp_generado:
                    st.session_state.usuarios.append({**st.session_state.datos_pre, "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS)
                    st.session_state.otp_generado = None
                    st.success("✅ Cuenta activada. ¡Ya puedes entrar!")
    with l1:
        lc, lp = st.text_input("Correo"), st.text_input("Clave", type="password")
        if st.button("Iniciar Sesión"):
            u = next((u for u in st.session_state.usuarios if u['correo'] == lc and u['password'] == hash_password(lp)), None)
            if u: 
                st.session_state.usuario_identificado = u
                st.rerun()

elif rol_vista == "🔐 Administración":
    au, ap = st.text_input("Admin User"), st.text_input("Admin Pass", type="password")
    if st.button("Entrar Admin"):
        if au == "admin" and ap == "admin123":
            st.session_state.usuario_identificado = {"correo": "ADMIN", "rol": "admin"}
            st.rerun()
