import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    /* Fondo General */
    .stApp {
        background-color: #f4f7f9;
    }

    /* Tarjetas de Paquetes (Efecto Elevación) */
    .p-card {
        background: white;
        padding: 22px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 6px solid #0080FF;
        margin-bottom: 18px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .p-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }

    /* Títulos y Bienvenida */
    .welcome-text {
        color: #1E3A8A;
        font-weight: 800;
        font-size: 28px;
        letter-spacing: -0.5px;
        margin-bottom: 15px;
    }

    /* Botones Profesionales */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #0080FF;
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #005BB5;
        box-shadow: 0 4px 12px rgba(0,128,255,0.3);
        color: white;
    }

    /* Encabezados de Estados en Resumen */
    .state-header {
        background: linear-gradient(90deg, #1E3A8A 0%, #0080FF 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        margin-top: 25px;
        margin-bottom: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
    }

    /* Estilo de las métricas */
    [data-testid="stMetricValue"] {
        color: #1E3A8A;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE ARCHIVOS Y MOTOR ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
PRECIO_POR_KG = 5.0

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

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.markdown(f"**Socio Activo:**\n{st.session_state.usuario_identificado.get('nombre', 'Admin')}")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Sección del Sistema:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro”")
    st.caption("“No eres herramienta, eres evolución”")

# --- 4. INTERFAZ DE ADMINISTRADOR ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control Logístico")
    
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Registro Inicial (Peso Mensajero)")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo del Cliente")
            f_pes = st.number_input("Peso Mensajero (Kg)", min_value=0.0, step=0.1)
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli and f_cor:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), 
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False,
                        "Monto_USD": f_pes * PRECIO_POR_KG, "Estado": "RECIBIDO ALMACEN PRINCIPAL",
                        "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    st.success(f"✅ Guía {f_id} guardada exitosamente.")
                else: st.error("Por favor complete los campos obligatorios.")

    with t_val:
        st.subheader("Validación de Peso en Almacén")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado', False)]
        if pendientes:
            guia_v = st.selectbox("Guía para validar:", [p["ID_Barra"] for p in pendientes])
            paq = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_v), None)
            if paq:
                peso_m = paq.get('Peso_Mensajero', 0.0)
                st.info(f"Cliente: {paq['Cliente']} | Peso Mensajero: {peso_m} Kg")
                peso_real = st.number_input("Peso Real de Báscula (Kg)", min_value=0.0, value=float(peso_m))
                if st.button("Confirmar Validación"):
                    paq['Peso_Almacen'] = peso_real
                    paq['Validado'] = True
                    paq['Monto_USD'] = peso_real * PRECIO_POR_KG
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    if abs(peso_real - peso_m) > 0.1:
                        st.error(f"🚨 ALERTA: Diferencia de peso crítica ({abs(peso_real - peso_m):.2f} Kg)")
                    else: st.success("✅ Peso validado correctamente.")
                    st.rerun()
        else: st.info("No hay paquetes pendientes de pesaje en almacén.")

    with t_cob:
        st.subheader("Gestión de Cobros y Morosidad")
        if st.session_state.inventario:
            df_c = pd.DataFrame(st.session_state.inventario)
            hoy = datetime.now()
            df_c['Estatus_Pago'] = df_c.apply(lambda r: 'PAGADO' if r['Pago'] == 'PAGADO' else ('ATRASADO' if (hoy - pd.to_datetime(r['Fecha_Registro'])).days > 15 else 'PENDIENTE'), axis=1)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.write("🟢 **PAGADOS**")
                st.dataframe(df_c[df_c['Estatus_Pago'] == 'PAGADO'][['ID_Barra', 'Monto_USD']], hide_index=True)
            with c2:
                st.write("🟡 **PENDIENTES**")
                df_p = df_c[df_c['Estatus_Pago'] == 'PENDIENTE']
                st.dataframe(df_p[['ID_Barra', 'Monto_USD']], hide_index=True)
                for idx, r in df_p.iterrows():
                    if st.button(f"Cobrar {r['ID_Barra']}", key=f"c_{idx}"):
                        st.session_state.inventario[idx]['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()
            with c3:
                st.write("🔴 **ATRASADOS (+15 días)**")
                st.dataframe(df_c[df_c['Estatus_Pago'] == 'ATRASADO'][['ID_Barra', 'Monto_USD']], hide_index=True)

    with t_est:
        st.subheader("Tránsito de Mercancía")
        if st.session_state.inventario:
            sel = st.selectbox("Seleccione Guía:", [p["ID_Barra"] for p in st.session_state.inventario])
            n_st = st.selectbox("Cambiar Estado a:", ["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for p in st.session_state.inventario:
                    if p["ID_Barra"] == sel: p["Estado"] = n_st
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_aud:
        st.subheader("Registro Maestro")
        if st.session_state.inventario:
            st.dataframe(pd.DataFrame(st.session_state.inventario), use_container_width=True)

    with t_res:
        st.subheader("Resumen de Operación por Fase")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            col1, col2, col3 = st.columns(3)
            col1.metric("Kilos Validados", f"{df['Peso_Almacen'].sum():.1f} Kg")
            col2.metric("Paquetes Totales", len(df))
            col3.metric("Ingresos Reales", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")
            
            for est, ico in zip(["RECIBIDO ALMACEN PRINCIPAL", "EN TRANSITO", "ENTREGADO"], ["📦", "✈️", "🏠"]):
                df_f = df[df['Estado'] == est]
                st.markdown(f'<div class="state-header">{ico} {est} ({len(df_f)})</div>', unsafe_allow_html=True)
                if not df_f.empty: st.dataframe(df_f[['ID_Barra', 'Cliente', 'Peso_Almacen', 'Pago']], hide_index=True, use_container_width=True)

# --- 5. PANEL DEL CLIENTE (ACTUALIZADO CON FILTROS Y PAGOS) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido nuevamente, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    # Filtrar paquetes del cliente
    mis_p = [p for p in st.session_state.inventario if p.get('Correo', '').lower() == u['correo'].lower()]
    
    if mis_p:
        df_mis_p = pd.DataFrame(mis_p)
        hoy = datetime.now()
        
        # Sincronización de lógica de pago con la del administrador
        df_mis_p['Estatus_Pago'] = df_mis_p.apply(
            lambda r: 'PAGADO' if r['Pago'] == 'PAGADO' else 
            ('ATRASADO' if (hoy - pd.to_datetime(r['Fecha_Registro'])).days > 15 else 'PENDIENTE'), 
            axis=1
        )

        # 📊 Métricas de resumen para el cliente (Socio)
        c1, c2, c3 = st.columns(3)
        total_deuda = df_mis_p[df_mis_p['Estatus_Pago'] != 'PAGADO']['Monto_USD'].sum()
        c1.metric("Total por Pagar", f"${total_deuda:.2f}")
        c2.metric("Paquetes en Proceso", len(df_mis_p[df_mis_p['Estado'] != 'ENTREGADO']))
        c3.metric("Entregados", len(df_mis_p[df_mis_p['Estado'] == 'ENTREGADO']))

        st.write("---")

        # 🔍 Buscador y Filtro
        col_bus, col_fil = st.columns([2, 1])
        search = col_bus.text_input("🔍 Buscar Guía")
        filtro_pago = col_fil.selectbox("Filtrar por estatus:", ["Todos", "Pendientes/Atrasados", "Pagados"])

        # Aplicar filtros a la visualización
        display_df = df_mis_p.copy()
        if search:
            display_df = display_df[display_df['ID_Barra'].str.contains(search, case=False)]
        if filtro_pago == "Pendientes/Atrasados":
            display_df = display_df[display_df['Estatus_Pago'] != 'PAGADO']
        elif filtro_pago == "Pagados":
            display_df = display_df[display_df['Estatus_Pago'] == 'PAGADO']

        # 📦 Visualización de Tarjetas Dinámicas
        for _, p in display_df.iterrows():
            # Color dinámico: Verde (Pagado), Rojo (Atrasado), Azul/Amarillo (Pendiente)
            border_color = "#28a745" if p['Estatus_Pago'] == 'PAGADO' else ("#dc3545" if p['Estatus_Pago'] == 'ATRASADO' else "#FFCC00")
            
            st.markdown(f"""
                <div class="p-card" style="border-left: 6px solid {border_color};">
                    <div style="display: flex; justify-content: space-between;
