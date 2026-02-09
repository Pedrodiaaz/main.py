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
st.set_page_config(page_title="IACargo.io | Portal Verificado", layout="wide", page_icon="🚀")

# Archivos de base de datos
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

# --- CONFIGURACIÓN DE CORREO (EMISOR) ---
# IMPORTANTE: Usa una "Contraseña de Aplicación" de Google
EMAIL_EMISOR = "tu_correo@gmail.com" 
PASS_EMISOR = "tu_contraseña_de_aplicacion" 

# --- 2. MOTOR DE FUNCIONES ---

def enviar_otp_estilizado(correo_destino, codigo):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"{codigo} es tu código de verificación - IACargo.io"
        msg['From'] = f"IACargo.io Support <{EMAIL_EMISOR}>"
        msg['To'] = correo_destino

        # Diseño del Correo en HTML
        html = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #0080FF; padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">IACargo.io</h1>
                </div>
                <div style="padding: 30px; text-align: center;">
                    <h2 style="color: #2E4053;">Verifica tu cuenta</h2>
                    <p>Gracias por unirte a nuestra plataforma logística. Utiliza el siguiente código para completar tu registro:</p>
                    <div style="background-color: #f4f4f4; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #0080FF;">{codigo}</span>
                    </div>
                    <p style="font-size: 14px; color: #777;">Este código expirará en breve. Si no solicitaste este registro, ignora este correo.</p>
                </div>
                <div style="background-color: #f9f9f9; padding: 15px; text-align: center; font-size: 12px; color: #999;">
                    <p>“La existencia es un milagro”</p>
                    <p>&copy; 2024 IACargo.io - Evolución en Logística</p>
                </div>
            </div>
        </body>
        </html>
        """
        parte_html = MIMEText(html, 'html')
        msg.attach(parte_html)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_EMISOR, PASS_EMISOR)
        server.sendmail(EMAIL_EMISOR, correo_destino, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar correo: {e}")
        return False

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def cargar_datos(archivo):
    if os.path.exists(archivo):
        return pd.read_csv(archivo).to_dict('records')
    return []

def guardar_datos(datos, archivo):
    pd.DataFrame(datos).to_csv(archivo, index=False)

# Inicializar estados de sesión
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

# --- 3. INTERFAZ VISUAL ---

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    st.write("---")
    
    if st.session_state.usuario_identificado:
        st.success(f"Sesión: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol = st.radio("Sección:", ["🔑 Clientes", "🔐 Administración"])
    
    st.write("---")
    st.caption("“La existencia es un milagro”")

# ==========================================
# PORTAL CLIENTES
# ==========================================
if not st.session_state.usuario_identificado and rol == "🔑 Clientes":
    st.title("📦 Acceso de Clientes")
    tab_log, tab_reg = st.tabs(["Iniciar Sesión", "Crear Cuenta"])

    with tab_reg:
        if not st.session_state.otp_generado:
            st.subheader("Regístrate")
            u_cor = st.text_input("Correo Electrónico")
            u_pas = st.text_input("Contraseña", type="password")
            if st.button("Solicitar Código de Verificación"):
                if u_cor and u_pas:
                    if any(u['correo'] == u_cor for u in st.session_state.usuarios):
                        st.error("Este correo ya está registrado.")
                    else:
                        codigo = str(random.randint(100000, 999999))
                        if enviar_otp_estilizado(u_cor, codigo):
                            st.session_state.otp_generado = codigo
                            st.session_state.datos_pre_registro = {"correo": u_cor, "password": hash_password(u_pas)}
                            st.success("📩 Código enviado. Revisa tu bandeja de entrada.")
                            st.rerun()
                else:
                    st.error("Por favor completa los campos.")
        else:
            st.subheader("Verificación de Seguridad")
            otp_input = st.text_input("Introduce el código de 6 dígitos enviado:")
            c_b1, c_b2 = st.columns(2)
            if c_b1.button("Verificar y Finalizar"):
                if otp_input == st.session_state.otp_generado:
                    nuevo_u = {"correo": st.session_state.datos_pre_registro['correo'], 
                               "password": st.session_state.datos_pre_registro['password'], 
                               "rol": "cliente"}
                    st.session_state.usuarios.append(nuevo_u)
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS)
                    st.session_state.otp_generado = None
                    st.success("✅ ¡Cuenta verificada! Ya puedes iniciar sesión.")
                else:
                    st.error("Código incorrecto.")
            if c_b2.button("Cancelar"):
                st.session_state.otp_generado = None
                st.rerun()

    with tab_log:
        st.subheader("Ingreso al Portal")
        l_cor = st.text_input("Correo", key="l_cor")
        l_pas = st.text_input("Contraseña", type="password", key="l_pas")
        if st.button("Entrar"):
            user = next((u for u in st.session_state.usuarios if u['correo'] == l_cor and u['password'] == hash_password(l_pas)), None)
            if user:
                st.session_state.usuario_identificado = user
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")

# (Si el usuario es cliente, se muestra su tabla de envíos...)
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Mis Envíos")
    mis_p = [p for p in st.session_state.inventario if str(p['Correo']).lower() == st.session_state.usuario_identificado['correo'].lower()]
    if mis_p:
        st.dataframe(pd.DataFrame(mis_p)[["ID_Barra", "Estado", "Monto_USD", "Pago"]], use_container_width=True)
    else:
        st.info("No tienes paquetes registrados aún.")

# ==========================================
# PANEL ADMINISTRATIVO
# ==========================================
elif rol == "🔐 Administración":
    st.title("🔐 Control Administrativo")
    if not st.session_state.usuario_identificado or st.session_state.usuario_identificado['rol'] != "admin":
        u_adm = st.text_input("Usuario")
        p_adm = st.text_input("Clave", type="password")
        if st.button("Acceder"):
            if u_adm == "admin" and p_adm == "admin123":
                st.session_state.usuario_identificado = {"correo": "ADMIN", "rol": "admin"}
                st.rerun()
    else:
        # Pestañas de Admin con el buscador en Auditoría que pediste
        t_reg, t_pes, t_cob, t_aud = st.tabs(["📝 Registro", "⚖️ Pesaje", "💰 Cobros", "📊 Auditoría"])
        
        with t_reg:
            with st.form("admin_reg"):
                id_p = st.text_input("ID Paquete")
                cli = st.text_input("Cliente")
                cor = st.text_input("Correo Cliente (Vincular)")
                peso = st.number_input("Peso (Kg)")
                if st.form_submit_button("Registrar"):
                    nuevo = {"ID_Barra": id_p, "Cliente": cli, "Correo": cor, "Peso_Origen": peso, 
                             "Peso_Almacen": 0.0, "Monto_USD": peso*PRECIO_POR_KG, "Estado": "Recogido", 
                             "Pago": "PENDIENTE", "Fecha_Registro": datetime.now().strftime("%Y-%m-%d")}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success("Paquete registrado y vinculado.")

        with t_aud:
            st.subheader("Buscador de Auditoría")
            id_f = st.text_input("🔍 Filtrar por ID específico:")
            df = pd.DataFrame(st.session_state.inventario)
            if id_f:
                st.dataframe(df[df['ID_Barra'].astype(str).str.contains(id_f, case=False)])
            else:
                st.dataframe(df)
