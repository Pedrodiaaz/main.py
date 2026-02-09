import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime

# --- 1. CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="IACargo.io | Evolution System", layout="wide", page_icon="🚀")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .p-card {
        background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3); padding: 25px; border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1); margin-bottom: 20px;
    }
    .state-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #0080ff 100%);
        color: white; padding: 15px 25px; border-radius: 15px; margin: 20px 0;
    }
    .stButton>button {
        border-radius: 12px; height: 3em; font-weight: 700; text-transform: uppercase;
    }
    /* Estilo para botón eliminar */
    .btn-eliminar button {
        background-color: #ff4b4b !important; color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE DATOS ---
ARCHIVO_DB = "inventario_logistica.csv"
ARCHIVO_USUARIOS = "usuarios_iacargo.csv"
ARCHIVO_PAPELERA = "papelera_iacargo.csv"
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
if 'papelera' not in st.session_state: st.session_state.papelera = cargar_datos(ARCHIVO_PAPELERA)
if 'usuarios' not in st.session_state: st.session_state.usuarios = cargar_datos(ARCHIVO_USUARIOS)
if 'usuario_identificado' not in st.session_state: st.session_state.usuario_identificado = None

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    else: st.title("🚀 IACargo.io")
    st.write("---")
    if st.session_state.usuario_identificado:
        st.success(f"Socio: {st.session_state.usuario_identificado.get('nombre', 'Usuario')}")
        if st.button("Cerrar Sesión"):
            st.session_state.usuario_identificado = None
            st.rerun()
    else:
        rol_vista = st.radio("Navegación:", ["🔑 Portal Clientes", "🔐 Administración"])
    st.write("---")
    st.caption("“La existencia es un milagro” | “Evolución”")

# --- 4. INTERFAZ ADMIN ---
if st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "admin":
    st.title("⚙️ Consola de Control Logístico")
    tabs = st.tabs(["📝 REGISTRO", "⚖️ VALIDACIÓN", "💰 COBROS", "✈️ ESTADOS", "🔍 AUDITORÍA/EDICIÓN", "📊 RESUMEN"])
    t_reg, t_val, t_cob, t_est, t_aud, t_res = tabs

    with t_reg:
        st.subheader("Nuevo Ingreso")
        with st.form("reg_form", clear_on_submit=True):
            f_id = st.text_input("ID Tracking")
            f_cli = st.text_input("Cliente")
            f_cor = st.text_input("Correo")
            f_pes = st.number_input("Peso Inicial (Kg)", min_value=0.0, step=0.1)
            if st.form_submit_button("Registrar"):
                nuevo = {"ID_Barra": f_id, "Cliente": f_cli, "Correo": f_cor.lower().strip(), "Peso_Mensajero": f_pes, "Peso_Almacen": 0.0, "Validado": False, "Monto_USD": f_pes*5, "Estado": "RECIBIDO ALMACEN PRINCIPAL", "Pago": "PENDIENTE", "Fecha_Registro": datetime.now()}
                st.session_state.inventario.append(nuevo)
                guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                st.success("Registrado.")

    with t_aud:
        col_aud1, col_aud2 = st.columns([3, 1])
        with col_aud1: st.subheader("Historial y Corrección")
        with col_aud2: 
            ver_papelera = st.checkbox("🗑️ Ver Papelera")

        if ver_papelera:
            st.warning("Mostrando paquetes anulados/eliminados")
            if st.session_state.papelera:
                df_pap = pd.DataFrame(st.session_state.papelera)
                st.dataframe(df_pap, use_container_width=True)
                guia_res = st.selectbox("Seleccione ID para RESTAURAR:", [p["ID_Barra"] for p in st.session_state.papelera])
                if st.button("♻️ Restaurar Paquete"):
                    paq_r = next((p for p in st.session_state.papelera if p["ID_Barra"] == guia_res), None)
                    st.session_state.inventario.append(paq_r)
                    st.session_state.papelera = [p for p in st.session_state.papelera if p["ID_Barra"] != guia_res]
                    guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                    guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA)
                    st.success("Paquete restaurado."); st.rerun()
            else: st.info("La papelera está vacía.")
        else:
            busq = st.text_input("🔍 Buscar guía:", key="aud_search")
            df_aud = pd.DataFrame(st.session_state.inventario)
            if busq: df_aud = df_aud[df_aud['ID_Barra'].astype(str).str.contains(busq, case=False)]
            st.dataframe(df_aud, use_container_width=True)
            
            st.write("---")
            st.markdown("### 🛠️ Panel de Edición y Anulación")
            guia_a_editar = st.selectbox("Seleccione ID:", [p["ID_Barra"] for p in st.session_state.inventario], key="edit_box")
            paq_edit = next((p for p in st.session_state.inventario if p["ID_Barra"] == guia_a_editar), None)
            
            if paq_edit:
                c_e1, c_e2 = st.columns(2)
                with c_e1:
                    new_id = st.text_input("ID", value=paq_edit['ID_Barra'])
                    new_cli = st.text_input("Cliente", value=paq_edit['Cliente'])
                with c_e2:
                    new_pes_a = st.number_input("Peso Almacén", value=float(paq_edit.get('Peso_Almacen', 0.0)))
                    new_pago = st.selectbox("Pago", ["PENDIENTE", "PAGADO"], index=0 if paq_edit['Pago'] == "PENDIENTE" else 1)
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("💾 Guardar Cambios"):
                        paq_edit.update({'ID_Barra': new_id, 'Cliente': new_cli, 'Peso_Almacen': new_pes_a, 'Pago': new_pago})
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        st.success("Actualizado."); st.rerun()
                with col_btn2:
                    st.markdown('<div class="btn-eliminar">', unsafe_allow_html=True)
                    if st.button("🗑️ Eliminar / Anular Paquete"):
                        st.session_state.papelera.append(paq_edit)
                        st.session_state.inventario = [p for p in st.session_state.inventario if p["ID_Barra"] != guia_a_editar]
                        guardar_datos(st.session_state.inventario, ARCHIVO_DB)
                        guardar_datos(st.session_state.papelera, ARCHIVO_PAPELERA)
                        st.warning("Paquete movido a la papelera."); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    # El resto de pestañas (Val, Cob, Est, Res) se mantienen igual...
    with t_val:
        st.subheader("Validación")
        pendientes = [p for p in st.session_state.inventario if not p.get('Validado', False)]
        if pendientes:
            gv = st.selectbox("Guía:", [p["ID_Barra"] for p in pendientes])
            p_v = next(p for p in pendientes if p["ID_Barra"] == gv)
            pr = st.number_input("Peso Real", value=float(p_v['Peso_Mensajero']))
            if st.button("Confirmar"):
                p_v.update({'Peso_Almacen': pr, 'Validado': True, 'Monto_USD': pr*5})
                guardar_datos(st.session_state.inventario, ARCHIVO_DB); st.rerun()

    with t_res:
        st.subheader("Resumen General")
        if st.session_state.inventario:
            df = pd.DataFrame(st.session_state.inventario)
            st.metric("Total Recaudado", f"${df[df['Pago']=='PAGADO']['Monto_USD'].sum():.2f}")
            st.dataframe(df)

# --- PANEL CLIENTE Y ACCESO ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido, {u["nombre"]}</div>', unsafe_allow_html=True)
    u_mail = str(u.get('correo', '')).lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    for p in mis_p:
        st.markdown(f'<div class="p-card"><h3>Guía: {p["ID_Barra"]}</h3><p>Estado: {p["Estado"]}</p></div>', unsafe_allow_html=True)

else:
    # Login básico (como el anterior)
    t_login, t_sign = st.tabs(["Ingresar", "Registro"])
    with t_login:
        le = st.text_input("Correo"); lp = st.text_input("Clave", type="password")
        if st.button("Entrar"):
            if le == "admin" and lp == "admin123":
                st.session_state.usuario_identificado = {"nombre": "Admin", "rol": "admin"}; st.rerun()
            usr = next((u for u in st.session_state.usuarios if u['correo'] == le.lower() and u['password'] == hash_password(lp)), None)
            if usr: st.session_state.usuario_identificado = usr; st.rerun()
