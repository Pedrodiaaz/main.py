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
# RECUERDA: Pon tus credenciales reales aquí para que el registro funcione
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
        return pd.read_csv(archivo).to_dict('records')
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
        st.success(f"Conectado: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.rerun()
        rol_actual = "Sesion Activa"
    else:
        rol_actual = st.radio("Sección:", ["🔑 Clientes", "🔐 Administración"])

# --- LÓGICA DE PORTALES ---

# PORTAL DE CLIENTE LOGUEADO
if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Mis Envíos Privados")
    mis_p = [p for p in st.session_state.inventario if str(p['Correo']).lower() == st.session_state.usuario_identificado['correo'].lower()]
    if mis_p:
        st.dataframe(pd.DataFrame(mis_p)[["ID_Barra", "Estado", "Monto_USD", "Pago", "Fecha_Registro"]], use_container_width=True)
    else:
        st.info("Aún no tienes paquetes vinculados a tu correo.")

# PANEL ADMIN LOGUEADO
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Panel Administrativo Central")
    t_reg, t_pes, t_cob, t_aud = st.tabs(["📝 Registro", "⚖️ Pesaje", "💰 Cobros", "📊 Auditoría"])
    
    with t_reg:
        with st.form("admin_reg"):
            id_p = st.text_input("ID Paquete")
            cli = st.text_input("Nombre Cliente")
            cor = st.text_input("Correo Cliente (Vincular)")
            peso = st.number_input("Peso Inicial (Kg)", min_value=0.0)
            if st.form_submit_button("Guardar Registro"):
                if id_p and cor:
                    nuevo = {"ID_Barra": id_p, "Cliente": cli, "Correo": cor, "Peso_Origen": peso, 
                             "Peso_Almacen": 0.0, "Monto_USD": peso*PRECIO_POR_KG, "Estado": "En espera", 
                             "Pago": "PENDIENTE", "Fecha_Registro": datetime.now().strftime("%Y-%m-%d")}
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success("✅ Paquete registrado y vinculado.")
                else:
                    st.error("ID y Correo son obligatorios.")

    with t_pes:
        st.subheader("⚖️ Validación de Pesaje")
        ids_pendientes = [p["ID_Barra"] for p in st.session_state.inventario if p["Peso_Almacen"] == 0.0]
        if ids_pendientes:
            id_sel = st.selectbox("Seleccione ID para pesar:", ids_pendientes)
            p_real = st.number_input("Peso real detectado (Kg):", min_value=0.0)
            if st.button("Confirmar y Validar Peso"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == id_sel:
                        p["Peso_Almacen"] = p_real
                        diff = abs(p_real - p["Peso_Origen"])
                        if diff > (p["Peso_Origen"] * 0.05):
                            p["Estado"] = "🔴 RETENIDO: DISCREPANCIA"
                        else:
                            p["Estado"] = "🟢 VERIFICADO"
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        st.success("Operación de pesaje completada.")
                        st.rerun()
        else:
            st.info("No hay paquetes pendientes de pesaje real.")

    with t_cob:
        st.subheader("💰 Gestión de Cobros")
        pendientes = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
        if pendientes:
            for p in pendientes:
                c_c1, c_c2 = st.columns([3, 1])
                c_c1.write(f"**ID:** {p['ID_Barra']} | **Cliente:** {p['Cliente']} | **Monto:** ${p['Monto_USD']:.2f}")
                if c_c2.button("Marcar Pagado", key=f"pay_{p['ID_Barra']}"):
                    p["Pago"] = "PAGADO"
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success(f"Pago de {p['ID_Barra']} registrado.")
                    st.rerun()
        else:
            st.success("No hay pagos pendientes.")

    with t_aud:
        st.subheader("📊 Auditoría e Inventario")
        id_f = st.text_input("🔍 Buscar por ID:")
        df = pd.DataFrame(st.session_state.inventario)
        if id_f and not df.empty:
            st.dataframe(df[df['ID_Barra'].astype(str).str.contains(id_f, case=False)], use_container_width=True)
        else:
            st.dataframe(df, use_container_width=True)

# ACCESO CLIENTE (SIN LOGUEAR)
elif rol_actual == "🔑 Clientes":
    st.title("📦 Acceso Clientes")
    t_log, t_sig = st.tabs(["Login", "Registro"])
    
    with t_sig:
        if not st.session_state.otp_generado:
            u_c = st.text_input("Correo")
            u_p = st.text_input("Clave", type="password")
            if st.button("Obtener Código"):
                codigo = str(random.randint(100000, 999999))
                if enviar_otp_estilizado(u_c, codigo):
                    st.session_state.otp_generado = codigo
                    st.session_state.datos_pre_registro = {"correo": u_c, "password": hash_password(u_p)}
                    st.rerun()
        else:
            otp_v = st.text_input("Ingrese Código Enviado")
            if st.button("Verificar"):
                if otp_v == st.session_state.otp_generado:
                    st.session_state.usuarios.append({"correo": st.session_state.datos_pre_registro['correo'], "password": st.session_state.datos_pre_registro['password'], "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS)
                    st.session_state.otp_generado = None
                    st.success("Cuenta verificada.")
    
    with t_log:
        l_c = st.text_input("Correo Electrónico")
        l_p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            user = next((u for u in st.session_state.usuarios if u['correo'] == l_c and u['password'] == hash_password(l_p)), None)
            if user:
                st.session_state.usuario_identificado = user
                st.rerun()

# ACCESO ADMIN (SIN LOGUEAR)
elif rol_actual == "🔐 Administración":
    st.title("🔐 Acceso Administrativo")
    a_u = st.text_input("Usuario")
    a_p = st.text_input("Clave", type="password")
    if st.button("Acceder"):
        if a_u == "admin" and a_p == "admin123":
            st.session_state.usuario_identificado = {"correo": "ADMIN", "rol": "admin"}
            st.rerun()
        else:
            st.error("Credenciales Inválidas")
