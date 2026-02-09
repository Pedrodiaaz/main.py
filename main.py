import streamlit as st
import pandas as pd
import os
import smtplib
import random
import hashlib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IACargo.io | Sistema Integral", layout="wide", page_icon="🚀")

# Archivos de base de datos
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

# --- CONFIGURACIÓN DE CORREO (EMISOR) ---
EMAIL_EMISOR = "tu_correo@gmail.com" 
PASS_EMISOR = "tu_contraseña_de_aplicacion" 

# --- 2. MOTOR DE FUNCIONES ---
def enviar_otp_estilizado(correo_destino, codigo):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{codigo} es tu código de verificación - IACargo.io"
        msg['From'] = f"IACargo.io Support <{EMAIL_EMISOR}>"
        msg['To'] = correo_destino
        html = f"""
        <html>
        <body style="font-family: Arial; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #eee; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #0080FF; padding: 20px; text-align: center; color: white;">
                    <h1>IACargo.io</h1>
                </div>
                <div style="padding: 30px; text-align: center;">
                    <h2>Código de Verificación</h2>
                    <p>Usa el siguiente código para activar tu cuenta:</p>
                    <h1 style="letter-spacing: 5px; color: #0080FF;">{codigo}</h1>
                </div>
            </div>
        </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_EMISOR, PASS_EMISOR)
        server.sendmail(EMAIL_EMISOR, correo_destino, msg.as_string())
        server.quit()
        return True
    except:
        return False

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            return pd.read_csv(archivo).to_dict('records')
        except: return []
    return []

def guardar_datos(datos, archivo):
    pd.DataFrame(datos).to_csv(archivo, index=False)

# Inicialización de sesión
if 'inventario' not in st.session_state:
    st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state:
    st.session_state.usuario_identificado = None
if 'otp_generado' not in st.session_state:
    st.session_state.otp_generado = None
if 'datos_pre_registro' not in st.session_state:
    st.session_state.datos_pre_registro = None

# --- 3. INTERFAZ ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    st.write("---")
    
    if st.session_state.usuario_identificado:
        st.success(f"Sesión: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión", key="logout_btn"):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_actual = st.radio("Sección:", ["🔑 Clientes", "🔐 Administración"], key="main_rol")

# --- LÓGICA DE NAVEGACIÓN ---

# A. CLIENTE LOGUEADO
if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Mis Envíos")
    correo_u = st.session_state.usuario_identificado['correo'].lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == correo_u]
    if mis_p:
        st.dataframe(pd.DataFrame(mis_p)[["ID_Barra", "Estado", "Monto_USD", "Pago"]], use_container_width=True)
    else:
        st.info("No hay paquetes vinculados a este correo.")

# B. ADMIN LOGUEADO
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Gestión Admin")
    t_reg, t_pes, t_cob, t_aud = st.tabs(["📝 Registro", "⚖️ Pesaje", "💰 Cobros", "📊 Auditoría"])
    
    with t_reg:
        with st.form("form_reg_admin"):
            id_p = st.text_input("ID Paquete")
            cli = st.text_input("Cliente")
            cor = st.text_input("Correo Cliente")
            peso = st.number_input("Peso (Kg)", min_value=0.0)
            if st.form_submit_button("Registrar"):
                st.session_state.inventario.append({
                    "ID_Barra": id_p, "Cliente": cli, "Correo": cor, "Peso_Origen": peso,
                    "Peso_Almacen": 0.0, "Monto_USD": peso*PRECIO_POR_KG, "Estado": "En espera",
                    "Pago": "PENDIENTE", "Fecha_Registro": datetime.now().strftime("%Y-%m-%d")
                })
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("Registrado.")
                st.rerun()

    with t_pes:
        pendientes = [p for p in st.session_state.inventario if p["Peso_Almacen"] == 0.0]
        if pendientes:
            id_sel = st.selectbox("ID a pesar:", [p["ID_Barra"] for p in pendientes])
            p_real = st.number_input("Peso real (Kg):", min_value=0.0)
            if st.button("Guardar Pesaje"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == id_sel:
                        p["Peso_Almacen"] = p_real
                        diff = abs(p_real - p["Peso_Origen"])
                        p["Estado"] = "🔴 DISCREPANCIA" if diff > (p["Peso_Origen"]*0.05) else "🟢 VERIFICADO"
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        st.rerun()
        else: st.info("Nada pendiente.")

    with t_cob:
        deuda = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
        for idx, p in enumerate(deuda):
            col1, col2 = st.columns([3, 1])
            col1.write(f"ID: {p['ID_Barra']} - ${p['Monto_USD']:.2f}")
            # AQUÍ ESTÁ LA SOLUCIÓN: Usamos idx para que el key sea siempre único
            if col2.button("Pagado", key=f"btn_pay_{p['ID_Barra']}_{idx}"):
                p["Pago"] = "PAGADO"
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.rerun()

    with t_aud:
        busq = st.text_input("Buscar ID:")
        df = pd.DataFrame(st.session_state.inventario)
        if busq and not df.empty:
            st.dataframe(df[df['ID_Barra'].astype(str).str.contains(busq, case=False)])
        else: st.dataframe(df)

# C. LOGIN CLIENTES
elif rol_actual == "🔑 Clientes":
    t_l, t_s = st.tabs(["Entrar", "Registrar"])
    with t_s:
        if not st.session_state.otp_generado:
            c_reg = st.text_input("Tu Correo")
            p_reg = st.text_input("Tu Clave", type="password")
            if st.button("Enviar Código"):
                otp = str(random.randint(100000, 999999))
                if enviar_otp_estilizado(c_reg, otp):
                    st.session_state.otp_generado = otp
                    st.session_state.datos_pre_registro = {"correo": c_reg, "password": hash_password(p_reg)}
                    st.rerun()
        else:
            val = st.text_input("Código de correo")
            if st.button("Validar Cuenta"):
                if val == st.session_state.otp_generado:
                    st.session_state.usuarios.append({**st.session_state.datos_pre_registro, "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS)
                    st.session_state.otp_generado = None
                    st.success("¡Listo!")
    with t_l:
        c_log = st.text_input("Correo")
        p_log = st.text_input("Clave", type="password")
        if st.button("Acceder"):
            u = next((u for u in st.session_state.usuarios if u['correo'] == c_log and u['password'] == hash_password(p_log)), None)
            if u: 
                st.session_state.usuario_identificado = u
                st.rerun()

# D. LOGIN ADMIN
elif rol_actual == "🔐 Administración":
    ad_u = st.text_input("Admin User")
    ad_p = st.text_input("Admin Pass", type="password")
    if st.button("Entrar Admin"):
        if ad_u == "admin" and ad_p == "admin123":
            st.session_state.usuario_identificado = {"correo": "ADMIN", "rol": "admin"}
            st.rerun()
