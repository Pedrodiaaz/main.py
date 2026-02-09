import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IACargo.io | Logística Inteligente", layout="wide", page_icon="🚀")

# --- 2. MOTOR DE DATOS Y PERSISTENCIA ---
PRECIO_POR_KG = 5.0
ARCHIVO_DB = "inventario_logistica.csv"

def cargar_datos():
    if os.path.exists(ARCHIVO_DB):
        try:
            return pd.read_csv(ARCHIVO_DB).to_dict('records')
        except:
            return []
    return []

def guardar_datos(datos):
    df = pd.DataFrame(datos)
    df.to_csv(ARCHIVO_DB, index=False)

# Inicializar inventario en la sesión
if 'inventario' not in st.session_state:
    st.session_state.inventario = cargar_datos()

# --- 3. BARRA LATERAL (LOGO E IDENTIDAD) ---
with st.sidebar:
    # Intentamos cargar el logo localmente
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    
    st.write("---")
    st.subheader("Selección de Portal")
    rol = st.radio("Acceder como:", ["🌐 Portal Cliente", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("v1.2 - Evolución Continua")

# ==========================================
# INTERFAZ 1: PORTAL CLIENTE (RASTREO)
# ==========================================
if rol == "🌐 Portal Cliente":
    st.markdown("<h1 style='color: #0080FF;'>📦 Seguimiento de Envíos</h1>", unsafe_allow_html=True)
    st.write("Bienvenido al portal de rastreo. Ingrese su código para conocer el estatus.")
    
    col_bus, _ = st.columns([2, 1])
    id_buscar = col_bus.text_input("ID de Tracking:", placeholder="Ej: IAC-101")
    
    if st.button("Consultar Estatus"):
        if id_buscar:
            paquete = next((p for p in st.session_state.inventario if str(p["ID_Barra"]).lower() == id_buscar.lower()), None)
            if paquete:
                st.success("✅ Paquete Localizado")
                c1, c2, c3 = st.columns(3)
                c1.metric("Estado", paquete['Estado'])
                c2.metric("Monto USD", f"${paquete['Monto_USD']:.2f}")
                c3.metric("Pago", paquete['Pago'])
                
                with st.expander("Ver Detalles del Envío"):
                    st.write(f"**Cliente:** {paquete['Cliente']}")
                    st.write(f"**Descripción:** {paquete['Descripcion']}")
                    st.write(f"**Fecha de Registro:** {paquete['Fecha_Registro']}")
            else:
                st.error("❌ El ID ingresado no existe en nuestro sistema.")
        else:
            st.warning("Por favor, ingrese un ID.")

# ==========================================
# INTERFAZ 2: PANEL ADMINISTRATIVO (ADMIN)
# ==========================================
else:
    st.markdown("<h1 style='color: #2E4053;'>🔐 Panel de Control Administrativo</h1>", unsafe_allow_html=True)
    
    # Seguridad de Acceso
    if 'admin_auth' not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        col_l, _ = st.columns([1, 2])
        with col_l:
            user = st.text_input("Usuario Admin")
            pw = st.text_input("Contraseña", type="password")
            if st.button("Ingresar al Sistema"):
                if user == "admin" and pw == "admin123":
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("Credenciales Incorrectas")
    else:
        # Botón para cerrar sesión en el sidebar
        if st.sidebar.button("🔒 Cerrar Sesión Admin"):
            st.session_state.admin_auth = False
            st.rerun()

        # Organización por Pestañas
        tab_reg, tab_pes, tab_cob, tab_aud = st.tabs([
            "📝 Registro", "⚖️ Pesaje", "💰 Cobros", "📊 Auditoría e Inventario"
        ])

        # --- TAREA: REGISTRO ---
        with tab_reg:
            st.subheader("Registrar Nueva Carga")
            with st.form("registro_form"):
                c1, c2 = st.columns(2)
                id_p = c1.text_input("ID Único del Paquete")
                cli = c1.text_input("Nombre del Cliente")
                cor = c2.text_input("Correo del Cliente")
                des = c2.text_area("Contenido / Descripción")
                peso_o = st.number_input("Peso Inicial en Báscula (Kg)", min_value=0.0, step=0.1)
                
                if st.form_submit_button("Guardar Registro"):
                    if id_p and cli:
                        monto = peso_o * PRECIO_POR_KG
                        nuevo = {
                            "ID_Barra": id_p, "Cliente": cli, "Correo": cor,
                            "Descripcion": des, "Peso_Origen": peso_o, "Peso_Almacen": 0.0,
                            "Monto_USD": monto, "Estado": "Recogido en casa", "Pago": "PENDIENTE",
                            "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        st.session_state.inventario.append(nuevo)
                        guardar_datos(st.session_state.inventario)
                        st.success(f"✅ Registrado con éxito. Cotización: ${monto:.2f}")
                    else:
                        st.error("El ID y el Cliente son campos obligatorios.")

        # --- TAREA: PESAJE ---
        with tab_pes:
            st.subheader("Validación de Peso en Almacén")
            pendientes_pesaje = [p["ID_Barra"] for p in st.session_state.inventario if p["Peso_Almacen"] == 0.0]
            
            if pendientes_pesaje:
                id_v = st.selectbox("Seleccione ID para pesaje real:", pendientes_pesaje)
                peso_a = st.number_input("Peso Real detectado (Kg):", min_value=0.0, step=0.1)
                if st.button("Confirmar y Validar"):
                    for p in st.session_state.inventario:
                        if p["ID_Barra"] == id_v:
                            p["Peso_Almacen"] = peso_a
                            diff = abs(peso_a - p["Peso_Origen"])
                            # Margen de error del 5%
                            if diff > (p["Peso_Origen"] * 0.05):
                                p["Estado"] = "🔴 RETENIDO: DISCREPANCIA"
                                st.warning(f"⚠️ Alerta: Diferencia de {diff:.2f} Kg.")
                            else:
                                p["Estado"] = "🟢 VERIFICADO"
                                st.success("✅ Peso validado correctamente.")
                            guardar_datos(st.session_state.inventario)
                            st.rerun()
            else:
                st.info("No hay paquetes pendientes por pesar.")

        # --- TAREA: COBROS ---
        with tab_cob:
            st.subheader("Gestión de Pagos Pendientes")
            deudores = [p for p in st.session_state.inventario if p["Pago"] == "PENDIENTE"]
            if deudores:
                for p in deudores:
                    col_d1, col_d2 = st.columns([3, 1])
                    col_d1.info(f"ID: {p['ID_Barra']} | Cliente: {p['Cliente']} | Monto: ${p['Monto_USD']:.2f}")
                    if col_d2.button("Confirmar Pago", key=f"pago_{p['ID_Barra']}"):
                        p["Pago"] = "PAGADO"
                        guardar_datos(st.session_state.inventario)
                        st.success(f"Pago procesado para {p['ID_Barra']}")
                        st.rerun()
            else:
                st.success("🎉 Todos los paquetes están solventes.")

        # --- TAREA: AUDITORÍA CON BUSCADOR ---
        with tab_aud:
            st.subheader("📊 Control Total de Inventario")
            
            # Buscador específico solicitado
            col_search, _ = st.columns([1, 2])
            filtro_id = col_search.text_input("🔍 Buscar por ID específico:", placeholder="Escriba el ID...")

            if st.session_state.inventario:
                df = pd.DataFrame(st.session_state.inventario)
                
                # Aplicar filtro si existe
                if filtro_id:
                    df_final = df[df['ID_Barra'].astype(str).str.contains(filtro_id, case=False)]
                else:
                    df_final = df
                
                st.dataframe(df_final, use_container_width=True)
                
                st.write("---")
                st.download_button(
                    label="📥 Descargar Inventario Completo",
                    data=df.to_csv(index=False),
                    file_name="reporte_iacargo.csv",
                    mime="text/csv"
                )
            else:
                st.info("No hay registros en el inventario.")
