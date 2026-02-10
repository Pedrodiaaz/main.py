import streamlit as st
import pandas as pd
import os
import hashlib
import random
import string
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Management System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top left, #1e3a8a 0%, #0f172a 100%); color: #ffffff; }
    .logo-animado { font-style: italic !important; font-family: 'Georgia', serif; background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; }
    
    /* Contenedores */
    .stTabs, .stForm, [data-testid="stExpander"], .p-card {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px !important;
        padding: 20px; margin-bottom: 15px;
    }

    /* Botones Estilo Registro */
    div[data-testid="stForm"] button, .main-btn button {
        background-color: #2563eb !important; color: white !important;
        border-radius: 12px !important; font-weight: 700 !important;
        text-transform: uppercase !important; border: none !important;
        padding: 10px 20px !important;
    }

    .resumen-row {
        background-color: #ffffff !important; color: #1e293b !important;
        padding: 12px; border-bottom: 1px solid #cbd5e1;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 5px; border-radius: 8px;
    }

    .badge-atrasado { background: #ef4444; color: white; padding: 2px 8px; border-radius: 8px; font-size: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LÓGICA DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
PRECIO_UNITARIO = 5.0

def cargar_datos(archivo):
    if os.path.exists(archivo):
        df = pd.read_csv(archivo)
        if 'Fecha_Registro' in df.columns: df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'])
        return df.to_dict('records')
    return []

def guardar_datos(datos, archivo): pd.DataFrame(datos).to_csv(archivo, index=False)

if 'inventario' not in st.session_state: st.session_state.inventario = cargar_datos(ARCHIVO_DB)
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. DASHBOARD ADMINISTRADOR ---
def render_admin_dashboard():
    st.markdown('<h2 class="logo-animado">Panel de Administración Pro</h2>', unsafe_allow_html=True)
    
    t_reg, t_val, t_cob, t_est, t_aud, t_res = st.tabs([
        "📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA", "📊 RESUMEN"
    ])

    # 📝 PESTAÑA REGISTRO
    with t_reg:
        st.subheader("Entrada de Mercancía")
        col1, col2 = st.columns(2)
        with col1: tipo = st.selectbox("Tipo de Traslado", ["Aéreo", "Marítimo"])
        label_peso = "Peso Inicial (Kg)" if tipo == "Aéreo" else "Pies Cúbicos iniciales"
        
        with st.form("form_registro", clear_on_submit=True):
            f_id = st.text_input("Código de Tracking / Guía")
            f_cli = st.text_input("Nombre del Cliente")
            f_cor = st.text_input("Correo Electrónico")
            f_pes = st.number_input(label_peso, min_value=0.0, step=0.1)
            f_mod = st.selectbox("Modalidad", ["Pago Completo", "Cobro Destino", "Pago en Cuotas"])
            if st.form_submit_button("Registrar en Sistema"):
                if f_id and f_cli:
                    nuevo = {
                        "ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(),
                        "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False,
                        "Monto_USD": f_pes * PRECIO_UNITARIO, "Estado": "EN ALMACÉN",
                        "Pago": "PENDIENTE", "Modalidad": f_mod, "Tipo_Traslado": tipo,
                        "Abonado": 0.0, "Fecha_Registro": datetime.now()
                    }
                    st.session_state.inventario.append(nuevo)
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Registrado."); st.rerun()

    # ⚖️ PESTAÑA VALIDACIÓN (Detección de variaciones)
    with t_val:
        st.subheader("⚖️ Validación de Pesos")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado')]
        if pendientes:
            guia = st.selectbox("Guía a Validar", [p["ID_Barra"] for p in pendientes])
            p = next(x for x in pendientes if x["ID_Barra"] == guia)
            st.warning(f"Peso reportado en origen: {p['Peso_Mensajero']}")
            peso_real = st.number_input("Peso Real recibido en Almacén", min_value=0.0, value=float(p['Peso_Mensajero']))
            
            if abs(peso_real - p['Peso_Mensajero']) > 0.5:
                st.error("⚠️ ALARMA: Diferencia de peso detectada. Verifique contenido.")
                
            if st.button("Confirmar Recepción y Validar"):
                for item in st.session_state.inventario:
                    if item["ID_Barra"] == guia:
                        item.update({"Peso_Almacen": peso_real, "Validado": True, "Monto_USD": peso_real * PRECIO_UNITARIO})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Validado."); st.rerun()
        else: st.info("No hay paquetes pendientes de validación.")

    # 💰 PESTAÑA COBROS (Desglosada)
    with t_cob:
        st.subheader("Gestión de Cobros")
        c1, c2, c3 = st.columns(3)
        inv = st.session_state.inventario
        
        # Lógica de atrasados (más de 15 días sin pago total)
        fecha_limite = datetime.now() - timedelta(days=15)
        atrasados = [p for p in inv if p['Pago'] != 'PAGADO' and pd.to_datetime(p['Fecha_Registro']) < fecha_limite]
        pendientes = [p for p in inv if p['Pago'] == 'PENDIENTE' and p not in atrasados]
        pagados = [p for p in inv if p['Pago'] == 'PAGADO']

        c1.metric("Pagados", len(pagados))
        c2.metric("Pendientes", len(pendientes))
        c3.metric("ATRASADOS (>15d)", len(atrasados), delta_color="inverse")

        sel_pago = st.selectbox("Filtrar Cobros por:", ["Pendientes", "Atrasados", "Pagados"])
        lista = atrasados if sel_pago == "Atrasados" else pendientes if sel_pago == "Pendientes" else pagados
        
        for p in lista:
            with st.expander(f"{p['ID_Barra']} - {p['Cliente']}"):
                st.write(f"Total: ${p['Monto_USD']:.2f} | Abonado: ${p['Abonado']:.2f}")
                if p['Pago'] != 'PAGADO':
                    monto = st.number_input("Monto a abonar", 0.0, float(p['Monto_USD']-p['Abonado']), key=f"pay_{p['ID_Barra']}")
                    if st.button("Registrar Pago", key=f"btn_{p['ID_Barra']}"):
                        for item in st.session_state.inventario:
                            if item["ID_Barra"] == p["ID_Barra"]:
                                item['Abonado'] += monto
                                if item['Abonado'] >= item['Monto_USD']: item['Pago'] = 'PAGADO'
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    # ✈️ PESTAÑA ESTADOS
    with t_est:
        st.subheader("Control de Tránsito")
        if inv:
            guia_st = st.selectbox("Seleccione Guía", [p["ID_Barra"] for p in inv], key="st_guia")
            nuevo_est = st.selectbox("Cambiar Estatus a:", ["EN ALMACÉN", "EN TRÁNSITO", "ENTREGADO"])
            if st.button("Actualizar Estatus"):
                for item in st.session_state.inventario:
                    if item["ID_Barra"] == guia_st: item["Estado"] = nuevo_est
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.success("Estatus actualizado."); st.rerun()

    # 🔍 PESTAÑA AUDITORÍA
    with t_aud:
        st.subheader("Edición y Auditoría")
        busqueda = st.text_input("🔍 Buscar por Guía o Cliente")
        df_inv = pd.DataFrame(st.session_state.inventario)
        if busqueda and not df_inv.empty:
            df_inv = df_inv[df_inv['ID_Barra'].str.contains(busqueda, case=False) | df_inv['Cliente'].str.contains(busqueda, case=False)]
        st.dataframe(df_inv, use_container_width=True)
        
        if not df_inv.empty:
            guia_ed = st.selectbox("Seleccione para Acción", df_inv['ID_Barra'].tolist())
            col_ed1, col_ed2 = st.columns(2)
            if col_ed1.button("🗑️ Enviar a Papelera"):
                item = next(x for x in st.session_state.inventario if x["ID_Barra"] == guia_ed)
                st.session_state.papelera.append(item)
                st.session_state.inventario = [x for x in st.session_state.inventario if x["ID_Barra"] != guia_ed]
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA); st.rerun()

    # 📊 PESTAÑA RESUMEN (Seccionada)
    with t_res:
        st.subheader("Resumen de Carga")
        search_res = st.text_input("🔍 Buscar Caja (Solo Código)", key="res_search")
        for est_key, est_label in [("EN ALMACÉN", "📦 EN ALMACÉN"), ("EN TRÁNSITO", "✈️ EN TRÁNSITO"), ("ENTREGADO", "✅ ENTREGADO")]:
            items_est = [p for p in st.session_state.inventario if p['Estado'] == est_key]
            if search_res: items_est = [p for p in items_est if search_res.lower() in p['ID_Barra'].lower()]
            
            with st.expander(f"{est_label} ({len(items_est)})", expanded=True):
                for r in items_est:
                    icon = "✈️" if r.get('Tipo_Traslado') == "Aéreo" else "🚢"
                    st.markdown(f'''
                        <div class="resumen-row">
                            <div style="font-weight:bold; color:#2563eb;">{icon} {r["ID_Barra"]}</div>
                            <div>{r["Cliente"]}</div>
                            <div style="font-size: 0.9em; color: #64748b;">${r["Abonado"]:.2f} / ${r["Monto_USD"]:.2f}</div>
                        </div>
                    ''', unsafe_allow_html=True)

# --- 4. INTERFAZ CLIENTE (Dashboard) ---
def render_client_dashboard():
    u = st.session_state.usuario_identificado
    st.markdown(f'<h3>Panel de Cliente: {u["nombre"]}</h3>', unsafe_allow_html=True)
    mis_p = [p for p in st.session_state.inventario if p.get('Correo') == u['correo']]
    
    if not mis_p: st.info("No hay paquetes registrados con tu correo.")
    else:
        for p in mis_p:
            with st.container():
                st.markdown(f'<div class="p-card"><b>Guía: {p["ID_Barra"]}</b> | Estado: {p["Estado"]}', unsafe_allow_html=True)
                prog = (p['Abonado']/p['Monto_USD']) if p['Monto_USD'] > 0 else 0
                st.progress(prog)
                st.write(f"Pago: {p['Pago']} (${p['Abonado']} de ${p['Monto_USD']})")
                st.markdown('</div>', unsafe_allow_html=True)

# --- 5. LOGIN ---
def login():
    with st.sidebar:
        st.markdown('<h1 class="logo-animado" style="font-size:35px;">IACargo.io</h1>', unsafe_allow_html=True)
        if st.session_state.usuario_identificado:
            st.success(f"Usuario: {st.session_state.usuario_identificado['nombre']}")
            if st.button("Cerrar Sesión"): st.session_state.usuario_identificado = None; st.rerun()
        st.write("---")
        st.caption("“La existencia es un milagro”")

    if not st.session_state.usuario_identificado:
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.title("Acceso al Sistema")
            tab_in, tab_up = st.tabs(["Ingresar", "Registro"])
            with tab_in:
                with st.form("l_f"):
                    e = st.text_input("Correo"); p = st.text_input("Clave", type="password")
                    if st.form_submit_button("Entrar"):
                        if e == "admin" and p == "admin123":
                            st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
                        u = next((x for x in st.session_state.usuarios if x['correo'] == e.lower().strip() and x['password'] == hashlib.sha256(p.encode()).hexdigest()), None)
                        if u: st.session_state.usuario_identificado = u; st.rerun()
            with tab_up:
                with st.form("r_f"):
                    n = st.text_input("Nombre"); e2 = st.text_input("Email"); p2 = st.text_input("Password", type="password")
                    if st.form_submit_button("Crear Cuenta"):
                        st.session_state.usuarios.append({"nombre": n, "correo": e2.lower().strip(), "password": hashlib.sha256(p2.encode()).hexdigest(), "rol": "cliente"})
                        guardar_datos(st.session_state.usuarios, ARCHIVO_USUARIOS); st.success("Cuenta creada."); st.rerun()
    else:
        if st.session_state.usuario_identificado['rol'] == 'admin': render_admin_dashboard()
        else: render_client_dashboard()

login()
