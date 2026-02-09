# --- 5. PANEL DEL CLIENTE (VERSIÓN BLINDADA) ---
elif st.session_state.usuario_identificado and st.session_state.usuario_identificado.get('rol') == "cliente":
    u = st.session_state.usuario_identificado
    st.markdown(f'<div class="welcome-text">Bienvenido nuevamente, {u["nombre"]}</div>', unsafe_allow_html=True)
    
    c_izq, c_der = st.columns([2, 1])
    c_izq.subheader("📋 Estado de mis Envíos")
    search = c_der.text_input("🔍 Buscar por Número de Guía", key="user_search")
    
    # Filtramos primero por correo del usuario
    u_mail = str(u.get('correo', '')).lower()
    mis_p = [p for p in st.session_state.inventario if str(p.get('Correo', '')).lower() == u_mail]
    
    # Aplicamos el buscador con protección contra valores Nulos (None)
    if search:
        mis_p = [p for p in mis_p if p.get('ID_Barra') and search.lower() in str(p.get('ID_Barra')).lower()]
    
    if mis_p:
        for p in mis_p:
            with st.container():
                # Obtenemos los datos con .get por seguridad
                id_guia = p.get('ID_Barra', 'Sin ID')
                estado_paq = p.get('Estado', 'Procesando')
                fecha_paq = str(p.get('Fecha_Registro', 'N/A'))[:10]
                
                st.markdown(f"""
                <div class="p-card">
                    <h3 style='margin:0; color:#1E3A8A;'>Guía: {id_guia}</h3>
                    <p style='margin:5px 0;'>Estatus: <b>{estado_paq}</b></p>
                    <p style='margin:0; font-size:14px; color:#666;'>Fecha de Registro: {fecha_paq}</p>
                </div>
                """, unsafe_allow_html=True)
    else: 
        st.info("No se encontraron paquetes asociados a tu búsqueda o cuenta.")
