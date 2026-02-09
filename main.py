import streamlit as st
import pandas as pd
import os
import smtplib
import random
import hashlib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 1. CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="IACargo.io | Business Intelligence", layout="wide", page_icon="🚀")

# Estilos CSS Inyectados para asegurar el "Modelo" visual solicitado
st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    .stMetric { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eef; }
    .p-card { background: white; padding: 25px; border-radius: 15px; border-left: 6px solid #0080FF; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .status-active { color: #0080FF; font-weight: bold; text-transform: uppercase; }
    .step-box { background: #ebf5ff; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #b3d9ff; font-size: 0.9em; }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

# CONFIGURACIÓN DE CORREO
EMAIL_EMISOR = "tu_correo@gmail.com" 
PASS_EMISOR = "tu_contraseña_de_aplicacion" 

# --- 2. MOTOR DE DATOS Y COMUNICACIÓN ---

def enviar_notificacion(correo, asunto, html_content):
    try:
        msg = MIMEMultipart('alternative'); msg['Subject'] = asunto
        msg['From'] = f"IACargo.io <{EMAIL_EMISOR}>"; msg['To'] = correo
        msg.attach(MIMEText(html_content, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587); server.starttls()
        server.login(EMAIL_EMISOR, PASS_EMISOR)
        server.sendmail(EMAIL_EMISOR, correo, msg.as_string()); server.quit()
        return True
    except: return False

def cargar_datos(archivo):
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
        return df.to_dict('records')
    return []

def guardar_datos(datos, archivo):
    pd.DataFrame(datos).to_csv(archivo, index=False)

# Inicialización de Estados
if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. INTERFAZ LATERAL ---
with st.sidebar:
    st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Conectado: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        opcion = st.radio("Ir a:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")

# --- 4. PANEL DE USUARIO (CON LÍNEA DE TIEMPO VISUAL) ---

if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Seguimiento de Carga")
    u_mail = st.session_state.usuario_identificado['correo'].lower()
    mis_paquetes = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if mis_paquetes:
        for p in mis_paquetes:
            with st.container():
                st.markdown(f"""<div class="p-card">
                    <h3>Guía: {p['ID_Barra']}</h3>
                    <p>Estatus: <span class="status-active">{p['Estado']}</span></p>
                </div>""", unsafe_allow_html=True)
                
                # --- LÓGICA DE LÍNEA DE TIEMPO (STEPPER) ---
                progreso = 0
                s1, s2, s3 = "⚪", "⚪", "⚪"
                if "RECIBIDO" in p['Estado']: progreso, s1 = 33, "🔵"
                elif "TRANSITO" in p['Estado']: progreso, s1, s2 = 66, "🔵", "🔵"
                elif "ENTREGADO" in p['Estado']: progreso, s1, s2, s3 = 100, "🔵", "🔵", "🔵"
                
                st.progress(progreso)
                col1, col2, col3 = st.columns(3)
                col1.markdown(f"<div class='step-box'>{s1}<br><b>RECIBIDO</b><br>Almacén</div>", unsafe_allow_html=True)
                col2.markdown(f"<div class='step-box'>{s2}<br><b>EN TRÁNSITO</b><br>Hacia destino</div>", unsafe_allow_html=True)
                col3.markdown(f"<div class='step-box'>{s3}<br><b>ENTREGADO</b><br>Finalizado</div>", unsafe_allow_html=True)
                st.write(f"**Detalles Económicos:** Costo: ${p['Monto_USD']} | Pago: {p['Pago']}")
                st.write("---")
    else:
        st.info("Aún no tienes paquetes registrados con este correo.")

# --- 5. PANEL DE ADMINISTRACIÓN (DASHBOARD + RESUMEN) ---

elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Consola de Control Total")
    # AQUÍ ESTÁ LA PESTAÑA RESUMEN QUE SOLICITASTE
    t_res, t_reg, t_est, t_cob = st.tabs(["📈 RESUMEN", "📝 REGISTRO", "⚖️ ESTADOS", "💰 COBROS"])

    # 1. PESTAÑA RESUMEN (Gráficos y Métricas)
    with t_res:
        st.subheader("Análisis de Rendimiento")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
            
            periodo = st.selectbox("Evaluar:", ["Semanal", "Mensual", "Anual"])
            rango = {"Semanal": 7, "Mensual": 30, "Anual": 365}[periodo]
            df_f = df[df['Fecha_Registro'] >= (datetime.now() - timedelta(days=rango))]

            m1, m2, m3 = st.columns(3)
            m1.metric("Clientes Atendidos", len(df_f['Correo'].unique()))
            m2.metric("Kilos Movidos", f"{df_f['Peso_Origen'].sum():.1f} Kg")
            m3.metric("Recaudación", f"${df_f[df_f['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")

            st.write("### Relación Registros vs Ingresos")
            # Gráfico de barras relacional
            chart_data = df_f.groupby(df_f['Fecha_Registro'].dt.date).agg({'ID_Barra':'count', 'Monto_USD':'sum'})
            st.bar_chart(chart_data)
        else: st.info("Sin datos para mostrar resumen.")

    # 2. PESTAÑA REGISTRO
    with t_reg:
        with st.form("registro_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            id_i = c1.text_input("ID Guía")
            cl_i = c1.text_input("Nombre Cliente")
            co_i = c2.text_input("Correo Cliente")
            pe_i = c2.number_input("Peso (Kg)", min_value=0.0)
            if st.form_submit_button("Guardar en Sistema"):
                nuevo = {"ID_Barra": id_i, "Cliente": cl_i, "Correo": co_i, "Peso_Origen": pe_i,
                         "Monto_USD": pe_i*PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                         "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("✅ Registrado con éxito.")

    # 3. PESTAÑA ESTADOS (Cambia línea de tiempo y envía correo)
    with t_est:
        st.subheader("Actualizar Ubicación de Carga")
        if st.session_state.inventario:
            ids = [p["ID_Barra"] for p in st.session_state.inventario]
            sel = st.selectbox("Seleccione Guía:", ids)
            nuevo_e = st.selectbox("Nuevo Estado:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar y Notificar"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel:
                        p["Estado"] = nuevo_e
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        enviar_notificacion(p['Correo'], "Actualización de tu carga", f"Tu paquete {sel} ahora está: {nuevo_e}")
                        st.success("Estado actualizado.")
                        st.rerun()

    # 4. PESTAÑA COBROS
    with t_cob:
        pendientes = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
        for idx, p in enumerate(pendientes):
            col1, col2 = st.columns([3, 1])
            col1.info(f"{p['ID_Barra']} | {p['Cliente']} | ${p['Monto_USD']}")
            if col2.button("Confirmar Pago", key=f"pay_{idx}"):
                p["Pago"] = "PAGADO"
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                enviar_notificacion(p['Correo'], "Pago Recibido", f"Gracias por tu pago del paquete {p['ID_Barra']}")
                st.rerun()

# --- 6. LÓGICA DE ACCESO (LOGIN) ---
elif opcion == "🔑 Portal Clientes":
    # (Aquí va tu lógica de Login/Registro con OTP que ya tenemos funcional)
    st.subheader("Acceso Clientes")
    # ... código de login ...
    # (Para no saturar, mantén la lógica de login que ya tenías)
