import streamlit as st
import pandas as pd

# Configuración profesional de la página
st.set_page_config(page_title="IACargo.io | Logística Inteligente", layout="wide", page_icon="🚀")

# --- BARRA LATERAL (SIDEBAR) ---
# RECUERDA: Cambia 'TU_USUARIO_GITHUB' por tu nombre real de usuario de GitHub
url_logo = "https://raw.githubusercontent.com/Pedrodiaaz/main.py/iacargo/main/logo.png"

with st.sidebar:
    try:
        st.image(url_logo, width=200)
    except:
        st.title("🚀 IACargo.io")
    
    st.write("---")
    st.title("Menú Principal")
    menu = ["🏠 Inicio", "📦 Rastreo de Carga", "👥 Gestión de Clientes", "🚢 Inventario/Flota", "🔐 Administración"]
    choice = st.selectbox("Navegación", menu)
    st.write("---")
    st.caption("Evolución en Logística v1.0")

# --- SECCIONES DEL MENÚ ---

if choice == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center; color: #0080FF;'>Bienvenido a IACargo.io</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px;'>La existencia es un milagro, la eficiencia es nuestra meta.</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Envíos Activos", "24", "+2")
    with col2:
        st.metric("Nuevas Solicitudes", "7", "-1")
    with col3:
        st.metric("Entregados hoy", "12", "+5")

elif choice == "📦 Rastreo de Carga":
    st.header("Seguimiento en Tiempo Real")
    guia = st.text_input("Introduce el Número de Guía o Tracking ID")
    if st.button("Rastrear Mercancía"):
        if guia:
            st.success(f"Buscando información para la guía: {guia}")
        else:
            st.warning("Por favor, introduce un número válido.")

elif choice == "👥 Gestión de Clientes":
    st.header("Base de Datos de Clientes")
    df_clientes = pd.DataFrame({
        'Cliente': ['Empresa A', 'Distribuidora B', 'Exportadora C'],
        'País': ['Venezuela', 'Panamá', 'España'],
        'Estado': ['Activo', 'Pendiente', 'Activo']
    })
    st.dataframe(df_clientes, use_container_width=True)

elif choice == "🚢 Inventario/Flota":
    st.header("Control de Unidades")
    st.write("Gestión de contenedores y espacios aéreos disponibles.")

elif choice == "🔐 Administración":
    st.header("Panel de Control Administrativo")
    
    # Sistema de Login de Admin
    if 'admin_auth' not in st.session_state:
        st.session_state['admin_auth'] = False

    if not st.session_state['admin_auth']:
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        if st.button("Entrar al Panel"):
            if usuario == "admin" and clave == "1234":
                st.session_state['admin_auth'] = True
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")
    else:
        if st.button("Cerrar Sesión Admin"):
            st.session_state['admin_auth'] = False
            st.rerun()

        st.write("---")
        st.subheader("⚖️ Validación de Peso y Volumen (Pre-Facturación)")
        
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            peso_cliente = st.number_input("Peso declarado por cliente (Kg)", min_value=0.0)
        with col_p2:
            peso_real = st.number_input("Peso real en báscula (Kg)", min_value=0.0)
        with col_p3:
            st.write("##")
            if st.button("Validar Diferencia"):
                diferencia = peso_real - peso_cliente
                if diferencia > 0:
                    st.error(f"Exceso detectado: +{diferencia:.2f} Kg")
                elif diferencia < 0:
                    st.warning(f"Menor al declarado: {diferencia:.2f} Kg")
                else:
                    st.success("El peso coincide perfectamente.")

        st.write("---")
        st.subheader("📏 Cálculo de Peso Volumétrico")
        cv1, cv2, cv3 = st.columns(3)
        largo = cv1.number_input("Largo (cm)", min_value=0.0)
        ancho = cv2.number_input("Ancho (cm)", min_value=0.0)
        alto = cv3.number_input("Alto (cm)", min_value=0.0)
        
        # Fórmula estándar para carga aérea (L*An*Al)/6000 o 5000 según la empresa
        peso_vol = (largo * ancho * alto) / 6000
        st.info(f"El peso volumétrico es: **{peso_vol:.2f} Kg**")
        
        if peso_vol > peso_real:
            st.warning(f"Atención: Se debe cobrar por Peso Volumétrico ({peso_vol:.2f} Kg)")
        else:
            st.success(f"Se debe cobrar por Peso Real ({peso_real:.2f} Kg)")
