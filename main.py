import streamlit as st
import pandas as pd

# Configuración profesional de la página
st.set_page_config(
    page_title="IACargo.io | Logística Inteligente", 
    layout="wide", 
    page_icon="🚀"
)

# --- CONFIGURACIÓN DEL LOGO ---
# Reemplaza TU_USUARIO_GITHUB por tu nombre de usuario en GitHub
url_logo = "https://raw.githubusercontent.com/Pedrodiaaz/iacargo/main/logo.png"

with st.sidebar:
    try:
        st.image(url_logo, width=220)
    except:
        st.title("🚀 IACargo.io")
    
    st.write("---")
    st.title("Menú Principal")
    menu = [
        "🏠 Inicio", 
        "📦 Rastreo de Carga", 
        "👥 Gestión de Clientes", 
        "🚢 Inventario/Flota", 
        "🔐 Administración"
    ]
    choice = st.selectbox("Navegación", menu)
    st.write("---")
    st.caption("Evolución en Logística v1.1")
    st.caption("“La existencia es un milagro”")

# --- LÓGICA DE SECCIONES ---

if choice == "🏠 Inicio":
    st.markdown("<h1 style='text-align: center; color: #0080FF;'>Bienvenido a IACargo.io</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>Conectando el mundo a través de tecnología y eficiencia.</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Métricas clave
    c1, c2, c3 = st.columns(3)
    c1.metric("Envíos Activos", "24", "+2")
    c2.metric("Pendientes por Validar", "5", "-1")
    c3.metric("Entregados Hoy", "12", "+5")
    
    st.image("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&q=80&w=1000", caption="Gestión Logística Global")

elif choice == "📦 Rastreo de Carga":
    st.header("Seguimiento en Tiempo Real")
    guia = st.text_input("Ingrese su Número de Tracking:")
    if st.button("Buscar"):
        if guia:
            st.info(f"Guía **{guia}**: En tránsito hacia destino final.")
            st.progress(70)
        else:
            st.warning("Por favor ingrese un código válido.")

elif choice == "👥 Gestión de Clientes":
    st.header("Directorio de Clientes")
    with st.expander("📝 Registrar Nuevo Cliente"):
        st.text_input("Nombre de Empresa")
        st.text_input("Contacto Principal")
        st.button("Guardar Cliente")
    
    # Datos de ejemplo
    data = {
        'Cliente': ['Inversiones G-7', 'Transportes Caracas', 'Global Cargo'],
        'País': ['Venezuela', 'Panamá', 'España'],
        'Status': ['Activo', 'En espera', 'Activo']
    }
    st.table(pd.DataFrame(data))

elif choice == "🚢 Inventario/Flota":
    st.header("Disponibilidad de Espacio")
    t1, t2 = st.tabs(["✈️ Aéreo", "🚢 Marítimo"])
    with t1:
        st.write("Cargueros disponibles: **3**")
    with t2:
        st.write("Contenedores en puerto: **15**")

elif choice == "🔐 Administración":
    st.header("Panel de Control Administrativo")
    
    # Login simple
    if 'auth' not in st.session_state:
        st.session_state['auth'] = False

    if not st.session_state['auth']:
        user = st.text_input("Usuario")
        pw = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if user == "admin" and pw == "1234":
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Acceso denegado")
    else:
        if st.sidebar.button("🔒 Cerrar Sesión"):
            st.session_state['auth'] = False
            st.rerun()

        st.success("Acceso Autorizado - Perfil Admin")
        st.write("---")
        
        # --- FUNCIÓN: VALIDACIÓN DE PESO (Lo que pediste) ---
        st.subheader("⚖️ Validación de Pesos (Báscula vs Declarado)")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            peso_dec = st.number_input("Peso declarado por cliente (Kg)", min_value=0.0)
            largo = st.number_input("Largo (cm)", min_value=0.0)
            ancho = st.number_input("Ancho (cm)", min_value=0.0)
            alto = st.number_input("Alto (cm)", min_value=0.0)
        
        with col_v2:
            peso_real = st.number_input("Peso real en báscula (Kg)", min_value=0.0)
            # Cálculo de peso volumétrico estándar (L*An*Al)/6000
            p_vol = (largo * ancho * alto) / 6000
            st.metric("Peso Volumétrico", f"{p_vol:.2f} Kg")
            
        if st.button("Validar y Procesar"):
            dif = peso_real - peso_dec
            if dif > 0:
                st.error(f"⚠️ Diferencia detectada: +{dif:.2f} Kg adicionales.")
            elif dif < 0:
                st.warning(f"ℹ️ El peso real es menor por {abs(dif):.2f} Kg.")
            else:
                st.success("✅ Los pesos coinciden perfectamente.")
            
            # Decisión de cobro
            peso_final = max(peso_real, p_vol)
            st.info(f"**Resultado de facturación:** Se debe cobrar por **{peso_final:.2f} Kg**.")
