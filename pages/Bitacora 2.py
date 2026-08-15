import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from io import BytesIO
from docx import Document
from docx.shared import Inches

st.set_page_config(
    page_title="Bitácora Digital - Diagnóstico, Gemelo Digital y Simulación",
    page_icon="📝",
    layout="wide"
)

# ------------------------------------------------------------------------------
# MÓDULO DE RECUPERACIÓN Y GUARDADO VÍA JSON
# ------------------------------------------------------------------------------
st.sidebar.title("💾 Gestión de Avance (JSON)")
st.sidebar.info(
    "Sube tu archivo .json previo para restaurar tu trabajo o descarga el estado "
    "actual para continuar desde casa."
)

# 1. Cargador de JSON
archivo_json_cargado = st.sidebar.file_uploader(
    "📂 Cargar Avance Guardado (.json)", type=["json"], key="uploader_json"
)

if archivo_json_cargado is not None:
    try:
        datos_recuperados = json.load(archivo_json_cargado)
        for k, v in datos_recuperados.items():
            st.session_state[k] = v
        st.sidebar.success("¡Avance cargado exitosamente! 🎉")
    except Exception as e:
        st.sidebar.error("Error al procesar el archivo JSON.")

# Inicialización de llaves por defecto en session_state si no existen
default_keys = {
    "est1_nombre": "",
    "est1_email": "",
    "est2_nombre": "",
    "est2_email": "",
    "ans_2_1": "",
    "ans_2_2": "",
    "cajeros_val": 1,
    "link_bpmn": "",
    "txt_flexsim": "",
    "diagnostico_equipo": "",
    "recomendaciones_equipo": ""
}
for k, v in default_keys.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.title("🏦 Bitácora Digital de Consultoría - Diagnóstico Operativo y Gemelo Digital")
st.caption("Herramienta de Recolección de Datos, Mapeo, Parametrización, Simulación en FlexSim, Resultados y Triangulación")
st.markdown("---")

# ------------------------------------------------------------------------------
# BLOQUE 1: REGISTRO DEL EQUIPO (CON CORREOS ELECTRÓNICOS)
# ------------------------------------------------------------------------------
st.header("📋 Bloque 1: Datos del Equipo Consultor")
col_e1, col_e2 = st.columns(2)

with col_e1:
    st.subheader("Estudiante 1")
    estudiante1 = st.text_input(
        "Nombre Estudiante 1",
        value=st.session_state["est1_nombre"],
        placeholder="Ingrese nombre completo...",
        key="est1_nombre"
    )
    email1 = st.text_input(
        "Correo Electrónico 1",
        value=st.session_state["est1_email"],
        placeholder="ejemplo@correo.com",
        key="est1_email"
    )

with col_e2:
    st.subheader("Estudiante 2")
    estudiante2 = st.text_input(
        "Nombre Estudiante 2",
        value=st.session_state["est2_nombre"],
        placeholder="Ingrese nombre completo...",
        key="est2_nombre"
    )
    email2 = st.text_input(
        "Correo Electrónico 2",
        value=st.session_state["est2_email"],
        placeholder="ejemplo@correo.com",
        key="est2_email"
    )

st.markdown("---")

# ------------------------------------------------------------------------------
# BLOQUE 2: MATRICES DE DATOS, GRÁFICAS Y ANÁLISIS DE CAMPO (AS-IS)
# ------------------------------------------------------------------------------
st.header("📊 Bloque 2: Digitación de Datos, Visualización y Diagnóstico Operativo (As-Is)")

st.subheader("Paso 2.1: Mezcla de Trámites, Tiempos de Atención y Autorización")

df_tramites_init = pd.DataFrame({
    "ID": [1, 2, 3, 4],
    "Tipo_Tramite": ["Tipico", "Pesada", "Largos", ""],
    "Mezcla_Pct": [50.0, 20.0, 10.0, 0.0],
    "Tiempo_Atencion_Seg": [120.0, 400.0, 2000.0, 0.0],
    "Prob_Autorizacion": [0.0, 30.0, 35.0, 0.0]
})
df_tramites = st.data_editor(df_tramites_init, num_rows="dynamic", use_container_width=True, key="ed_tramites")

df_t_valid = df_tramites[df_tramites['Tipo_Tramite'] != ""].copy()

buf_fig1_pareto = None
buf_fig1_prob = None

if not df_t_valid.empty and df_t_valid['Tiempo_Atencion_Seg'].sum() > 0:
    col_g1, col_g2 = st.columns(2)
    
    # --- GRÁFICA 1: PARETO DE TIEMPOS DE ATENCIÓN ---
    with col_g1:
        df_pareto = df_t_valid.sort_values(by='Tiempo_Atencion_Seg', ascending=False).reset_index(drop=True)
        df_pareto['Acumulado_Pct'] = (df_pareto['Tiempo_Atencion_Seg'].cumsum() / df_pareto['Tiempo_Atencion_Seg'].sum()) * 100

        fig_p, ax_p1 = plt.subplots(figsize=(5, 3.8))
        
        ax_p1.bar(df_pareto['Tipo_Tramite'], df_pareto['Tiempo_Atencion_Seg'], color='steelblue', alpha=0.8, width=0.4)
        ax_p1.set_ylabel('Tiempo Atención (seg)', color='steelblue', fontweight='bold')
        ax_p1.tick_params(axis='y', labelcolor='steelblue')
        plt.xticks(rotation=15)

        ax_p2 = ax_p1.twinx()
        ax_p2.plot(df_pareto['Tipo_Tramite'], df_pareto['Acumulado_Pct'], color='crimson', marker='D', linewidth=2)
        ax_p2.axhline(80, color='gray', linestyle='--', alpha=0.7, label='Línea 80%')
        ax_p2.set_ylabel('% Acumulado', color='crimson', fontweight='bold')
        ax_p2.set_ylim(0, 110)
        ax_p2.tick_params(axis='y', labelcolor='crimson')

        plt.title("Análisis de Pareto: Tiempos de Atención", fontsize=10, fontweight='bold')
        fig_p.tight_layout()
        st.pyplot(fig_p)

        buf_fig1_pareto = BytesIO()
        fig_p.savefig(buf_fig1_pareto, format="png")
        buf_fig1_pareto.seek(0)

    # --- GRÁFICA 2: PROBABILIDAD DE AUTORIZACIÓN ---
    with col_g2:
        fig_pr, ax_pr = plt.subplots(figsize=(5, 3.8))
        bars = ax_pr.bar(df_t_valid['Tipo_Tramite'], df_t_valid['Prob_Autorizacion'], color='darkseagreen', width=0.4)
        
        for bar in bars:
            yval = bar.get_height()
            ax_pr.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}%", ha='center', va='bottom', fontsize=9)

        ax_pr.set_ylabel('Probabilidad de Autorización (%)', fontweight='bold')
        ax_pr.set_xlabel('Tipo de Trámite', fontweight='bold')
        ax_pr.set_ylim(0, max(df_t_valid['Prob_Autorizacion'].max() + 15, 100))
        plt.xticks(rotation=15)
        plt.title("Probabilidad / Porcentaje de Autorización", fontsize=10, fontweight='bold')
        fig_pr.tight_layout()
        st.pyplot(fig_pr)

        buf_fig1_prob = BytesIO()
        fig_pr.savefig(buf_fig1_prob, format="png")
        buf_fig1_prob.seek(0)

    st.markdown("#### 🔍 Análisis Diagnóstico (Paso 2.1)")
    analisis_2_1 = st.text_area(
        "Redacte su diagnóstico sobre los tiempos (Pareto) y autorizaciones:",
        value=st.session_state["ans_2_1"],
        height=120,
        key="ans_2_1"
    )

else:
    st.info("ℹ️ Llene la tabla superior para generar las gráficas de Pareto y Autorizaciones.")

st.markdown("---")

st.subheader("Paso 2.2: Perfil Horario de Arribos (Demanda)")
df_arribos_init = pd.DataFrame({
    "Franja_Horaria": ["", "", "", "", "", ""],
    "Tipo_Perfil": ["", "", "", "", "", ""],
    "Clientes_Hora_Lambda": [0, 0, 0, 0, 0, 0]
})
df_arribos = st.data_editor(df_arribos_init, num_rows="dynamic", use_container_width=True, key="ed_arribos")
cajeros = st.number_input("Número de Cajeros Activos en Ventanilla (c):", min_value=1, max_value=20, value=int(st.session_state["cajeros_val"]), key="cajeros_val")

col_g2, col_t2 = st.columns([1.2, 1])
df_a_valid = df_arribos[df_arribos['Franja_Horaria'] != ""].copy()
buf_fig2 = None

if not df_t_valid.empty:
    ts_ponderado_calc = ((df_t_valid['Mezcla_Pct'] / 100) * df_t_valid['Tiempo_Atencion_Seg']).sum()
else:
    ts_ponderado_calc = 0

with col_g2:
    if not df_a_valid.empty and df_a_valid['Clientes_Hora_Lambda'].sum() > 0:
        fig2, ax = plt.subplots(figsize=(6, 4))
        ax.plot(df_a_valid['Franja_Horaria'], df_a_valid['Clientes_Hora_Lambda'], marker='o', color='navy', linewidth=2.5)
        ax.fill_between(df_a_valid['Franja_Horaria'], df_a_valid['Clientes_Hora_Lambda'], color='skyblue', alpha=0.3)

        if ts_ponderado_calc > 0:
            capacidad_sis_calc = (3600 / ts_ponderado_calc) * cajeros
            ax.axhline(y=capacidad_sis_calc, color='red', linestyle='--', linewidth=2, label=f'Capacidad Máx ({cajeros} cajeros)')

        ax.set_title("Arribos vs. Umbral de Capacidad", fontsize=10)
        ax.set_xlabel("Franja Horaria", fontweight='bold')
        ax.set_ylabel("Clientes / Hora", fontweight='bold')
        plt.xticks(rotation=25)
        ax.legend()
        ax.grid(True, linestyle=':', alpha=0.6)
        fig2.tight_layout()
        st.pyplot(fig2)
        
        buf_fig2 = BytesIO()
        fig2.savefig(buf_fig2, format="png")
        buf_fig2.seek(0)
    else:
        st.info("ℹ️ Llene la tabla y parámetros para ver la gráfica.")

with col_t2:
    st.markdown("#### 🔍 Análisis Diagnóstico (Paso 2.2)")
    analisis_2_2 = st.text_area("Redacte su diagnóstico sobre la demanda:", value=st.session_state["ans_2_2"], height=200, key="ans_2_2")

st.markdown("---")

# ------------------------------------------------------------------------------
# BLOQUE 3: CONSTRUCCIÓN DEL GEMELO DIGITAL (FLEXSIM)
# ------------------------------------------------------------------------------
st.header("🖥️ Bloque 3: Construcción del Gemelo Digital (FlexSim)")

st.subheader("3.1 Definición del Proceso")
col_b1, col_b2 = st.columns([1, 1])
with col_b1:
    link_bpmn = st.text_input("🔗 Link del Diagrama BPMN:", value=st.session_state["link_bpmn"], key="link_bpmn")
    imagen_bpmn = st.file_uploader("🖼️ Cargar Pantallazo BPMN:", type=["png", "jpg", "jpeg"], key="up_bpmn")
with col_b2:
    if imagen_bpmn: st.image(imagen_bpmn, use_container_width=True)

df_bpmn_init = pd.DataFrame({"Etapa_ID": [1,2,3], "Nombre_Etapa": ["","",""], "Actor_Responsable": ["","",""], "Tipo_Actividad": ["","",""], "Descripción_Operativa": ["","",""]})
df_bpmn = st.data_editor(df_bpmn_init, num_rows="dynamic", use_container_width=True, key="ed_bpmn")
st.markdown("---")

st.subheader("3.2 Parámetros del Gemelo Digital")
df_params_init = pd.DataFrame({"Etapa_ID": [1,2,3], "Nombre_Etapa": ["","",""], "Objeto_FlexSim": ["","",""], "Distribución_o_Regla": ["","",""], "Parámetros_Numéricos": ["","",""], "Recursos_Asignados": ["","",""]})
df_params = st.data_editor(df_params_init, num_rows="dynamic", use_container_width=True, key="ed_params")
st.markdown("---")

st.subheader("3.3 Modelo Construido en FlexSim")
col_f1, col_f2 = st.columns([1, 1])
with col_f1:
    imagen_flexsim = st.file_uploader("🖼️ Cargar Pantallazo del Layout FlexSim:", type=["png", "jpg", "jpeg"], key="up_flexsim")
    notas_flexsim = st.text_area("Observaciones sobre el modelo en FlexSim:", value=st.session_state["txt_flexsim"], height=150, key="txt_flexsim")
with col_f2:
    if imagen_flexsim: st.image(imagen_flexsim, use_container_width=True)
st.markdown("---")

st.subheader("3.4 Indicadores de Desempeño a Medir")
df_kpi_init = pd.DataFrame({"KPI_ID": [1,2,3], "Nombre_Indicador": ["","",""], "Unidad_Medida": ["","",""], "Objetivo": ["Minimizar","Minimizar","Minimizar"], "Meta_Verde": [0.0,0.0,0.0], "Critico_Rojo": [0.0,0.0,0.0]})
df_kpis = st.data_editor(df_kpi_init, num_rows="dynamic", use_container_width=True, column_config={"Objetivo": st.column_config.SelectboxColumn(options=["Minimizar", "Maximizar"])}, key="ed_kpis")
st.markdown("---")

# ------------------------------------------------------------------------------
# BLOQUE 4: SIMULACIÓN Y EVIDENCIAS
# ------------------------------------------------------------------------------
st.header("🎬 Bloque 4: Simulación y Evidencias de Ejecución (FlexSim)")
col_s1, col_s2 = st.columns(2)
with col_s1:
    imagen_sim_corrida = st.file_uploader("🖼️ Pantallazo de Simulación Ejecutándose:", type=["png", "jpg", "jpeg"], key="up_sim_corrida")
    if imagen_sim_corrida: st.image(imagen_sim_corrida, use_container_width=True)
with col_s2:
    imagen_dashboard_kpi = st.file_uploader("🖼️ Pantallazo del Dashboard de KPIs:", type=["png", "jpg", "jpeg"], key="up_dash_kpi")
    if imagen_dashboard_kpi: st.image(imagen_dashboard_kpi, use_container_width=True)
st.markdown("---")

# ------------------------------------------------------------------------------
# BLOQUE 5: TRIANGULACIÓN, DIAGNÓSTICO Y RECOMENDACIONES
# ------------------------------------------------------------------------------
st.header("⚖️ Bloque 5: Triangulación, Diagnóstico y Recomendaciones")

df_kpis_valid = df_kpis[df_kpis['Nombre_Indicador'] != ""].copy()
if not df_kpis_valid.empty:
    df_triang_init = pd.DataFrame({"KPI_ID": df_kpis_valid["KPI_ID"].tolist(), "Indicador_Clave": df_kpis_valid["Nombre_Indicador"].tolist(), "Modelo_Teorico_Calculado": [0.0]*len(df_kpis_valid), "Simulacion_FlexSim_Obtenido": [0.0]*len(df_kpis_valid)})
else:
    df_triang_init = pd.DataFrame({"KPI_ID": [1,2], "Indicador_Clave": ["",""], "Modelo_Teorico_Calculado": [0.0, 0.0], "Simulacion_FlexSim_Obtenido": [0.0, 0.0]})

df_triang_input = st.data_editor(df_triang_init, use_container_width=True, disabled=["KPI_ID", "Indicador_Clave"], key="ed_triangulacion_input")

resultados_triang = []
for i, row in df_triang_input.iterrows():
    calc, sim = row["Modelo_Teorico_Calculado"], row["Simulacion_FlexSim_Obtenido"]
    desv = sim - calc
    estado = "⚪ N/A"
    if not df_kpis_valid.empty and row["Indicador_Clave"] != "":
        kpi_info = df_kpis_valid[df_kpis_valid["KPI_ID"] == row["KPI_ID"]]
        if not kpi_info.empty:
            kpi_info = kpi_info.iloc[0]
            if kpi_info["Objetivo"] == "Minimizar":
                estado = "🟢 Verde" if sim <= kpi_info["Meta_Verde"] else ("🔴 Rojo" if sim >= kpi_info["Critico_Rojo"] else "🟡 Amarillo")
            else:
                estado = "🟢 Verde" if sim >= kpi_info["Meta_Verde"] else ("🔴 Rojo" if sim <= kpi_info["Critico_Rojo"] else "🟡 Amarillo")
    resultados_triang.append({"KPI_ID": row["KPI_ID"], "Indicador_Clave": row["Indicador_Clave"], "Modelo_Teorico_Calculado": calc, "Simulacion_FlexSim_Obtenido": sim, "Desviacion_o_Diferencia": desv, "Estado_Semaforo": estado})

df_triangulacion = pd.DataFrame(resultados_triang)
st.dataframe(df_triangulacion, use_container_width=True)

st.markdown("#### Diagnóstico y Recomendaciones")
diagnostico_equipo = st.text_area("Párrafo de Diagnóstico Consolidado:", value=st.session_state["diagnostico_equipo"], height=150, key="diagnostico_equipo")
recomendaciones_equipo = st.text_area("Propuestas y Recomendaciones de Intervención:", value=st.session_state["recomendaciones_equipo"], height=150, key="recomendaciones_equipo")
st.markdown("---")

# ------------------------------------------------------------------------------
# BOTÓN DE GUARDADO EN JSON (DESCARGA DE SEGURIDAD PARA LLEVAR A CASA)
# ------------------------------------------------------------------------------
datos_a_guardar = {
    "est1_nombre": st.session_state.get("est1_nombre", ""),
    "est1_email": st.session_state.get("est1_email", ""),
    "est2_nombre": st.session_state.get("est2_nombre", ""),
    "est2_email": st.session_state.get("est2_email", ""),
    "ans_2_1": st.session_state.get("ans_2_1", ""),
    "ans_2_2": st.session_state.get("ans_2_2", ""),
    "cajeros_val": st.session_state.get("cajeros_val", 1),
    "link_bpmn": st.session_state.get("link_bpmn", ""),
    "txt_flexsim": st.session_state.get("txt_flexsim", ""),
    "diagnostico_equipo": st.session_state.get("diagnostico_equipo", ""),
    "recomendaciones_equipo": st.session_state.get("recomendaciones_equipo", "")
}
json_data = json.dumps(datos_a_guardar, indent=4, ensure_ascii=False)

st.sidebar.download_button(
    label="💾 Descargar Estado Actual (.json)",
    data=json_data,
    file_name="avance_bitacora2.json",
    mime="application/json"
)

# ------------------------------------------------------------------------------
# BLOQUE 6: GENERACIÓN DE DOCUMENTO WORD
# ------------------------------------------------------------------------------
st.header("📄 Bloque 6: Exportación de Informe Final")
st.info("Haga clic en el botón inferior para generar y descargar un documento de Word (.docx) que consolida, numera y parafrasea automáticamente todas las tablas, gráficas y análisis redactados.")

def add_df_to_doc(df, doc):
    t = doc.add_table(df.shape[0]+1, df.shape[1])
    t.style = 'Table Grid'
    for j in range(df.shape[-1]):
        t.cell(0,j).text = str(df.columns[j])
        t.cell(0,j).paragraphs[0].runs[0].font.bold = True
    for i in range(df.shape[0]):
        for j in range(df.shape[-1]):
            t.cell(i+1,j).text = str(df.values[i,j])

def generar_word():
    doc = Document()
    doc.add_heading('Informe Técnico de Consultoría - Diagnóstico Operativo y Gemelo Digital', 0)
    
    p_equipo = doc.add_paragraph()
    p_equipo.add_run('Equipo Consultor:\n').bold = True
    
    nom1 = estudiante1 if estudiante1 else "No registrado"
    em1 = f" ({email1})" if email1 else ""
    p_equipo.add_run(f'• Estudiante 1: {nom1}{em1}\n')
    
    nom2 = estudiante2 if estudiante2 else "No registrado"
    em2 = f" ({email2})" if email2 else ""
    p_equipo.add_run(f'• Estudiante 2: {nom2}{em2}')
    
    # SECCIÓN 1
    doc.add_heading('1. Diagnóstico Operativo del Sistema Actual (As-Is)', level=1)
    doc.add_paragraph("Para comprender la situación actual del sistema, se realizó un mapeo de la demanda y de los procesos operativos. La Tabla 1 consolida los tipos de trámites identificados, su participación porcentual, el tiempo requerido y el porcentaje de autorización.")
    
    doc.add_heading('Tabla 1. Mezcla de Trámites, Tiempos Estándar y Autorizaciones', level=2)
    add_df_to_doc(df_tramites[df_tramites['Tipo_Tramite'] != ""], doc)
    
    if buf_fig1_pareto:
        doc.add_paragraph("\nLa Figura 1 presenta un análisis de Pareto que jerarquiza los trámites según el impacto de su tiempo de atención en la capacidad operativa.")
        doc.add_picture(buf_fig1_pareto, width=Inches(5.0))
        doc.add_paragraph("Figura 1. Diagrama de Pareto de Tiempos de Atención.", style='Caption')

    if buf_fig1_prob:
        doc.add_paragraph("\nLa Figura 2 detalla la tasa o probabilidad de autorización correspondiente a cada tipo de trámite.")
        doc.add_picture(buf_fig1_prob, width=Inches(5.0))
        doc.add_paragraph("Figura 2. Porcentaje de Autorización por Tipo de Trámite.", style='Caption')
    
    p_ans1 = doc.add_paragraph()
    p_ans1.add_run("Análisis Diagnóstico de Trámites: ").bold = True
    p_ans1.add_run(analisis_2_1 if analisis_2_1 else "No se registraron observaciones.")
    
    doc.add_paragraph("\nEn cuanto al flujo de usuarios, la Tabla 2 detalla el perfil de arribos segmentado por franjas horarias, lo que permite identificar los momentos críticos de operación.")
    doc.add_heading('Tabla 2. Perfil Horario de Arribos y Demanda', level=2)
    add_df_to_doc(df_arribos[df_arribos['Franja_Horaria'] != ""], doc)
    
    if buf_fig2:
        doc.add_paragraph("\nLa Figura 3 compara la tasa de llegada de los clientes frente a la capacidad máxima instalada del sistema.")
        doc.add_picture(buf_fig2, width=Inches(5.0))
        doc.add_paragraph("Figura 3. Curva de Arribos frente al Umbral de Capacidad Operativa.", style='Caption')
        
    p_ans2 = doc.add_paragraph()
    p_ans2.add_run("Análisis Diagnóstico de Arribos: ").bold = True
    p_ans2.add_run(analisis_2_2 if analisis_2_2 else "No se registraron observaciones.")
    
    # SECCIÓN 2
    doc.add_page_break()
    doc.add_heading('2. Diseño y Parametrización del Gemelo Digital (FlexSim)', level=1)
    doc.add_paragraph(f"El proceso lógico fue estructurado mediante un diagrama BPMN (Enlace de referencia: {link_bpmn if link_bpmn else 'N/A'}). Si bien el diagrama guía la lógica, las etapas específicas que componen el flujo en el simulador se describen detalladamente en la Tabla 3.")
    
    if imagen_bpmn:
        imagen_bpmn.seek(0)
        doc.add_picture(imagen_bpmn, width=Inches(5.5))
        doc.add_paragraph("Figura 4. Diagrama BPMN del proceso As-Is.", style='Caption')

    doc.add_heading('Tabla 3. Descripción de Etapas del Proceso', level=2)
    add_df_to_doc(df_bpmn[df_bpmn['Nombre_Etapa'] != ""], doc)
    
    doc.add_paragraph("\nPara transformar este esquema en un modelo 3D funcional, la Tabla 4 presenta la parametrización técnica ingresada en FlexSim, incluyendo reglas de ruteo, distribuciones estadísticas y asignación de recursos operativos.")
    doc.add_heading('Tabla 4. Parámetros Técnicos del Gemelo Digital', level=2)
    add_df_to_doc(df_params[df_params['Nombre_Etapa'] != ""], doc)
    
    if imagen_flexsim:
        doc.add_paragraph("\nLa Figura 5 muestra la construcción física (Layout) del modelo dentro del entorno virtual.")
        imagen_flexsim.seek(0)
        doc.add_picture(imagen_flexsim, width=Inches(5.5))
        doc.add_paragraph("Figura 5. Layout y entorno 3D del Gemelo Digital en FlexSim.", style='Caption')
    
    p_notas = doc.add_paragraph()
    p_notas.add_run("Observaciones sobre la construcción del modelo: ").bold = True
    p_notas.add_run(notas_flexsim if notas_flexsim else "No se registraron observaciones.")
    
    doc.add_paragraph("\nPara validar la eficiencia del sistema, se definieron metas operativas específicas estructuradas en la Tabla 5.")
    doc.add_heading('Tabla 5. Definición de KPIs y Umbrales Semafóricos', level=2)
    add_df_to_doc(df_kpis[df_kpis['Nombre_Indicador'] != ""], doc)
    
    # SECCIÓN 3
    doc.add_page_break()
    doc.add_heading('3. Ejecución de la Simulación y Triangulación de Resultados', level=1)
    
    doc.add_paragraph("Durante la corrida del modelo computacional, se extrajeron evidencias gráficas del comportamiento dinámico de las entidades y de los tableros de control.")
    if imagen_sim_corrida:
        imagen_sim_corrida.seek(0)
        doc.add_picture(imagen_sim_corrida, width=Inches(5))
        doc.add_paragraph("Figura 6. Ejecución del Gemelo Digital en tiempo real.", style='Caption')
    if imagen_dashboard_kpi:
        imagen_dashboard_kpi.seek(0)
        doc.add_picture(imagen_dashboard_kpi, width=Inches(5))
        doc.add_paragraph("Figura 7. Dashboard estadístico obtenido en FlexSim.", style='Caption')
        
    doc.add_paragraph("\nLa etapa culminante del análisis radica en la triangulación entre la base matemática teórica y la simulación por eventos discretos. La Tabla 6 consolida las desviaciones halladas y activa los semáforos de advertencia diseñados.")
    doc.add_heading('Tabla 6. Triangulación y Evaluación de KPIs', level=2)
    add_df_to_doc(df_triangulacion[df_triangulacion['Indicador_Clave'] != ""], doc)
    
    doc.add_heading('4. Conclusiones y Propuestas de Intervención', level=1)
    
    p_diag = doc.add_paragraph()
    p_diag.add_run("Diagnóstico Cuantitativo y Cualitativo Final: ").bold = True
    p_diag.add_run(diagnostico_equipo if diagnostico_equipo else "No se registraron observaciones.")
    
    p_rec = doc.add_paragraph()
    p_rec.add_run("\nRecomendaciones de Mejora Continua: ").bold = True
    p_rec.add_run(recomendaciones_equipo if recomendaciones_equipo else "No se registraron propuestas.")
    
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

st.download_button(
    label="📥 Generar y Descargar Documento Word (.docx)",
    data=generar_word(),
    file_name="Informe_Consultoria_Bitacora.docx",
    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)
