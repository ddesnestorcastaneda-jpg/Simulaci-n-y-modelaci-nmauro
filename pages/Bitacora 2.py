import streamlit as st
import json
import pandas as pd

st.title("📝 Bitácora con Autoguardado JSON")

# ------------------------------------------------------------------------------
# 1. RECUPERAR DATOS DESDE UN ARCHIVO JSON (Para trabajar desde casa)
# ------------------------------------------------------------------------------
st.sidebar.header("📂 Cargar Avance Guardado")
archivo_guardado = st.sidebar.file_uploader(
    "Sube tu archivo .json de la sesión anterior:", 
    type=["json"]
)

if archivo_guardado is not None:
    try:
        datos_recuperados = json.load(archivo_guardado)
        # Cargar los datos recuperados en el estado de la sesión
        for clave, valor in datos_recuperados.items():
            st.session_state[clave] = valor
        st.sidebar.success("¡Avance cargado exitosamente! 🎉")
    except Exception as e:
        st.sidebar.error("Error al leer el archivo JSON.")

# ------------------------------------------------------------------------------
# 2. CAMPOS DE LA BITÁCORA (Ejemplo de inputs)
# ------------------------------------------------------------------------------
st.header("📋 Información General")

# Nota: usamos el 'key' para vincular con session_state
nombre_est1 = st.text_input(
    "Nombre Estudiante 1", 
    value=st.session_state.get("est1_nombre", ""), 
    key="est1_nombre"
)

email_est1 = st.text_input(
    "Correo Estudiante 1", 
    value=st.session_state.get("est1_email", ""), 
    key="est1_email"
)

diagnostico = st.text_area(
    "Diagnóstico u Observaciones:", 
    value=st.session_state.get("txt_diagnostico", ""), 
    key="txt_diagnostico"
)

# ------------------------------------------------------------------------------
# 3. GUARDAR Y DESCARGAR EL AVANCE (Para llevarse a casa)
# ------------------------------------------------------------------------------
st.markdown("---")
st.header("💾 Guardar Trabajo Actual")

# Empaquetamos en un diccionario todos los campos a guardar
estado_actual = {
    "est1_nombre": st.session_state.get("est1_nombre", ""),
    "est1_email": st.session_state.get("est1_email", ""),
    "txt_diagnostico": st.session_state.get("txt_diagnostico", "")
}

# Convertimos el diccionario a formato JSON
json_string = json.dumps(estado_actual, indent=4, ensure_ascii=False)

# Botón para que el estudiante descargue su avance
st.download_button(
    label="📥 Descargar Avance (.json)",
    data=json_string,
    file_name="avance_bitacora.json",
    mime="application/json"
)
