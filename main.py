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
    .status-text { font-weight: bold; color: #0080FF; }
    .timeline-box { background: #f0f2f6; padding: 10px; border-radius: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

# CONFIGURACIÓN DE CORREO (Asegúrate de colocar tus credenciales reales)
EMAIL_EMISOR = "tu_correo@gmail.com" 
PASS_EMISOR = "tu_contraseña_de_aplicacion" 

# --- 2. MOTOR DE FUNCIONES ---

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
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Sesión: {st.session_state.usuario_identificado['correo']}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Sección:", ["🔑 Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. PANEL DE USUARIO (LÍNEA DE TIEMPO) ---

if st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "cliente":
    st.title("📦 Mis Envíos")
    u_mail = st.session_state.usuario_identificado['correo'].lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    if mis_p:
        for p in mis_p:
            with st.container():
                st.markdown(f"""<div class="p-card"><h3>Guía: {p['ID_Barra']}</h3><p>Estado: <span class="status-text">{p['Estado']}</span></p></div>""", unsafe_allow_html=True)
                
                # --- LINEA TEMPORAL VISUAL ---
                est = p['Estado']
                prog, p1, p2, p3 = 0, "⚪", "⚪", "⚪"
                if "RECIBIDO" in est: prog, p1 = 33, "🔵"
                elif "TRANSITO" in est: prog, p1, p2 = 66, "🔵", "🔵"
                elif "ENTREGADO" in est: prog, p1, p2, p3 = 100, "🔵", "🔵", "🔵"
                
                st.progress(prog)
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div class='timeline-box'>{p1}<br>RECIBIDO</div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='timeline-box'>{p2}<br>EN TRÁNSITO</div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='timeline-box'>{p3}<br>ENTREGADO</div>", unsafe_allow_html=True)
                st.write(f"**Detalles:** Peso: {p['Peso_Origen']} Kg | Pago: {p['Pago']} | Total: ${p['Monto_USD']}")
                st.write("---")
    else: st.info("No hay paquetes registrados bajo este correo.")

# --- 5. PANEL DE ADMINISTRACIÓN (RESUMEN + GESTIÓN) ---

elif st.session_state.usuario_identificado and st.session_state.usuario_identificado['rol'] == "admin":
    st.title("⚙️ Consola de Control")
    t_res, t_reg, t_pes, t_cob, t_aud = st.tabs(["📊 Resumen", "📝 Registro", "⚖️ Estados", "💰 Cobros", "🔍 Auditoría"])

    # --- PESTAÑA RESUMEN (ANALÍTICA) ---
    with t_res:
        if st.session_state.inventario:
            df_r = pd.DataFrame(st.session_state.inventario)
            df_r['Fecha_Registro'] = pd.to_datetime(df_r['Fecha_Registro'])
            periodo = st.selectbox("Rango:", ["Semanal", "Mensual", "Trimestral", "Anual"])
            dias = {"Semanal":7, "Mensual":30, "Trimestral":90, "Anual":365}[periodo]
            df_f = df_r[df_r['Fecha_Registro'] >= (datetime.now() - timedelta(days=dias))]

            c1, c2, c3 = st.columns(3)
            c1.metric("Clientes Únicos", len(df_f['Correo'].unique()))
            c2.metric("Masa Total (Kg)", f"{df_f['Peso_Origen'].sum():.1f}")
            c3.metric("Recaudación ($)", f"${df_f[df_f['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")

            st.write("### Relación de Registros y Cobros")
            st.bar_chart(df_f.groupby(df_f['Fecha_Registro'].dt.date).agg({'ID_Barra':'count', 'Monto_USD':'sum'}))
            
            st.write("### Top 5 Clientes por Volumen")
            st.table(df_f.groupby('Cliente')['Peso_Origen'].sum().sort_values(ascending=False).head(5))

    # --- PESTAÑA REGISTRO ---
    with t_reg:
        with st.form("reg_admin", clear_on_submit=True):
            st.subheader("Entrada de Mercancía")
            c1, c2 = st.columns(2)
            id_i = c1.text_input("ID Tracking")
            cl_i = c1.text_input("Cliente")
            co_i = c2.text_input("Correo")
            pe_i = c2.number_input("Peso (Kg)", min_value=0.0)
            if st.form_submit_button("Guardar"):
                st.session_state.inventario.append({
                    "ID_Barra": id_i, "Cliente": cl_i, "Correo": co_i, "Peso_Origen": pe_i,
                    "Monto_USD": pe_i*PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL", 
                    "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()
                })
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("✅ Finalizado con éxito: Paquete en sistema.")

    # --- PESTAÑA ESTADOS (NOTIFICACIONES) ---
    with t_pes:
        st.subheader("Gestión de Línea de Tiempo")
        if st.session_state.inventario:
            sel_id = st.selectbox("Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            nuevo_est = st.selectbox("Cambiar a:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar y Notificar Cliente"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel_id:
                        p["Estado"] = nuevo_est
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        html = f"<h2>Actualización de Envío</h2><p>Tu paquete <b>{sel_id}</b> cambió a: <b>{nuevo_est}</b>.</p>"
                        enviar_correo(p['Correo'], f"Estado de Paquete: {sel_id}", html)
                        st.success("✅ Estatus actualizado y correo enviado.")
                        st.rerun()

    # --- PESTAÑA COBROS (EXPORTACIÓN) ---
    with t_cob:
        s1, s2 = st.tabs(["❌ Pendientes", "✅ Pagados"])
        with s1:
            deudas = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
            for idx, p in enumerate(deudas):
                col_a, col_b = st.columns([3, 1])
                col_a.warning(f"{p['ID_Barra']} - {p['Cliente']} - ${p['Monto_USD']}")
                if col_b.button("Cobrar", key=f"pay_{idx}"):
                    p["Pago"] = "PAGADO"
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    enviar_correo(p['Correo'], "Confirmación de Pago", f"Recibimos el pago del paquete {p['ID_Barra']}")
                    st.rerun()
        with s2:
            df_p = pd.DataFrame([p for p in st.session_state.inventario if p["Pago"] == "PAGADO"])
            if not df_p.empty:
                st.dataframe(df_p[["ID_Barra", "Cliente", "Monto_USD", "Fecha_Registro"]], use_container_width=True)
                st.download_button("📥 Exportar Reporte Mensual (CSV)", df_p.to_csv(index=False).encode('utf-8'), "Cierre_IACargo.csv", "text/csv")

# --- 6. ACCESO LOGIN / REGISTRO (OTP) ---
elif rol_vista == "🔑 Clientes":
    st.title("Acceso Portal de Clientes")
    l1, l2 = st.tabs(["Entrar", "Registrarse"])
    with l2:
        if not st.session_state.otp_generado:
            cr = st.text_input("Correo")
            pr = st.text_input("Clave", type="password")
            if st.button("Obtener Código"):
                otp = str(random.randint(100000, 999999))
                if enviar_correo(cr, "Código de Activación", f"Tu código es: {otp}"):
                    st.session_state.otp_generado, st.session_state.datos_pre = otp, {"correo": cr, "password": hash_password(pr)}
                    st.rerun()
        else:
            v_otp = st.text_input("Código OTP")
            if st.button("Activar Cuenta"):
                if v_otp == st.session_state.otp_generado:
                    st.session_state.usuarios.append({**st.session_state.datos_pre, "rol": "cliente"})
                    guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS)
                    st.session_state.otp_generado = None
                    st.success("✅ Cuenta activada.")
    with l1:
        lc, lp = st.text_input("Email", key="lc"), st.text_input("Password", type="password", key="lp")
        if st.button("Ingresar"):
            u = next((u for u in st.session_state.usuarios if u['correo'] == lc and u['password'] == hash_password(lp)), None)
            if u: 
                st.session_state.usuario_identificado = u
                st.rerun()

elif rol_vista == "🔐 Administración":
    st.title("Consola Staff")
    au, ap = st.text_input("User"), st.text_input("Pass", type="password")
    if st.button("Entrar Admin"):
        if au == "admin" and ap == "admin123":
            st.session_state.usuario_identificado = {"correo": "ADMIN_SYSTEM", "rol": "admin"}
            st.rerun()
