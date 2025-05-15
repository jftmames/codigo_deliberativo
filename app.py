import os
import json
import streamlit as st
import openai
from modules.reasoning_tracker import ReasoningTracker
from modules.html_exporter import generate_html_report

# ---- 0. Configuración de página ----
st.set_page_config(
    page_title="Código Deliberativo Educativo",
    page_icon="🧠",
    layout="wide"
)

# ---- 1. Barra lateral – Ajustes ----
st.sidebar.header("🔧 Ajustes")
mode = st.sidebar.selectbox(
    "Perfil del usuario",
    ["Asistido (básico)", "Guiado (intermedio)", "Exploratorio (avanzado)"]
)
st.sidebar.markdown("---")
st.sidebar.info("Grupo de Investigación en IA.")

# ---- Opcional: Botón para reset total manual ----
if st.sidebar.button("🔄 Nuevo razonamiento / Reset"):
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.experimental_rerun()

# ---- 2. Título principal ----
st.title("🧠 Código Deliberativo para Pensamiento Crítico")
st.markdown(
    """
    Esta aplicación te guía paso a paso para **estructurar**, **explorar** y **evaluar**
    procesos de indagación críticos, usando un modelo de IA deliberativa.
    """
)

# ---- 3. Entrada de la pregunta ----
st.header("1. Define tu pregunta raíz")
example_questions = [
    "¿Es ético el uso de IA en diagnósticos médicos?",
    "¿Deberían las redes sociales regular cierto tipo de contenido?",
    "¿Cómo impacta la automatización en el mercado laboral juvenil?",
    "¿Es sostenible el modelo económico actual?",
    "¿Debe implementarse la renta básica universal?"
]
selected_example = st.selectbox("Ejemplos de preguntas", ["— Ninguno —"] + example_questions)
if selected_example != "— Ninguno —":
    root_question = selected_example
    st.markdown(f"**Pregunta seleccionada:** {root_question}")
else:
    root_question = st.text_input(
        "Escribe tu pregunta aquí",
        placeholder="Ej. ¿Es ético el uso de IA en diagnósticos médicos?",
    )
if not root_question:
    st.warning("🛈 Necesitamos una pregunta raíz para continuar.")
    st.stop()

# ---- RESET AUTOMÁTICO AL CAMBIAR DE PREGUNTA ----
if (
    "last_root_question" not in st.session_state
    or st.session_state["last_root_question"] != root_question
):
    # Resetea el tracker y los campos relacionados
    st.session_state["tracker"] = ReasoningTracker(root_question)
    st.session_state["last_root_question"] = root_question
    st.session_state.pop("node_selected", None)
    st.session_state.pop("respuestas_multiperspectiva", None)

# ---- 4. Preparación OpenAI ----
openai.api_key = os.getenv("OPENAI_API_KEY")
def chat(messages, max_tokens=500):
    return openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=max_tokens,
    )

# ---- 5. Definir marcos multiperspectiva ----
PERSPECTIVES = {
    "Ética": "Desde una perspectiva ética (deontología, utilitarismo, ética del cuidado)...",
    "Histórico-Social": "Desde una perspectiva histórica o sociopolítica relevante...",
    "Epistemológica": "Desde una perspectiva crítica epistemológica o filosófica..."
}

# ---- 6. Generación de árboles multiperspectiva ----
def generate_trees(root_question, chat_fn):
    trees = {}
    for marco, intro in PERSPECTIVES.items():
        prompt = (
            f"{intro}\n"
            f"Pregunta raíz: “{root_question}”\n"
            "1. Identifica 3–5 subpreguntas necesarias para el análisis crítico.\n"
            "2. Organízalas en estructura jerárquica.\n"
            "Devuelve solo JSON: {{ 'node': '...', 'children': [ ... ] }}"
        )
        resp = chat_fn([{"role": "system", "content": prompt}], max_tokens=600)
        try:
            trees[marco] = json.loads(resp.choices[0].message.content)
        except Exception:
            trees[marco] = {"node": "Error al generar", "children": []}
    return trees

with st.spinner("Generando árboles multiperspectiva…"):
    trees = generate_trees(root_question, chat)

# ---- 7. Visualización y navegación ----
st.header("2. Explora los árboles desde diferentes perspectivas")
marco = st.selectbox("Elige perspectiva de análisis", list(trees.keys()))
st.subheader(f"Árbol de subpreguntas ({marco})")

def build_dot(node):
    node_name = node.get("node", "<sin etiqueta>")
    node_state = st.session_state["tracker"].log.get("node_states", {}).get(node_name, {}).get("state", "Abierta")
    color_map = {
        "Abierta": "limegreen",
        "Resuelta": "deepskyblue",
        "En disputa": "orange",
        "Suspendida": "gray"
    }
    emoji_map = {
        "Abierta": "🟢",
        "Resuelta": "🔵",
        "En disputa": "🟠",
        "Suspendida": "⚪"
    }
    color = color_map.get(node_state, "black")
    emoji = emoji_map.get(node_state, "🟢")
    label = f"{emoji} {node_name}"

    dot = f'"{label}" [style=filled, fillcolor={color}, shape=box, fontname="Arial", fontsize=14];\n'
    for child in node.get("children", []):
        c_label = child.get("node", "<sin etiqueta>")
        child_state = st.session_state["tracker"].log.get("node_states", {}).get(c_label, {}).get("state", "Abierta")
        c_emoji = emoji_map.get(child_state, "🟢")
        c_label_full = f"{c_emoji} {c_label}"
        dot += f'"{label}" -> "{c_label_full}";\n'
        dot += build_dot(child)
    return dot

root = trees[marco]
dot = f'digraph G {{\nrankdir=TB;\nnode [style=filled, fontname="Arial"];\n{build_dot(root)}}}'
st.graphviz_chart(dot, use_container_width=True)

with st.expander("Ver leyenda de colores del grafo"):
    st.markdown(
        """
        **🟢 Abierta**: Subpregunta aún en análisis  
        **🔵 Resuelta**: Subpregunta cerrada/resuelta  
        **🟠 En disputa**: Subpregunta en debate o sin consenso  
        **⚪ Suspendida**: Subpregunta postergada/no relevante  
        """
    )

with st.expander("Mostrar subpreguntas en formato de lista"):
    def render_list(node, indent=0):
        node_name = node.get('node', '<sin título>')
        node_state = st.session_state["tracker"].log.get("node_states", {}).get(node_name, {}).get("state", "Abierta")
        emoji = {"Abierta":"🟢", "Resuelta":"🔵", "En disputa":"🟠", "Suspendida":"⚪"}.get(node_state,"🟢")
        st.markdown(" " * indent * 2 + f"- {emoji} **{node_name}**")
        for c in node.get("children", []):
            render_list(c, indent + 1)
    render_list(root)

# ---- 8. Selección de nodo, estado y justificación ----
node_selected = st.text_input("¿Sobre qué subpregunta quieres profundizar?")
if st.button("Seleccionar subpregunta"):
    st.session_state["tracker"].log_event("seleccion", node_selected, marco=marco)
    st.session_state["node_selected"] = node_selected

if "node_selected" in st.session_state:
    st.subheader("Estado epistémico de la subpregunta")
    estados = {
        "Abierta": "🟢 Abierta",
        "Resuelta": "🔵 Resuelta",
        "En disputa": "🟠 En disputa",
        "Suspendida": "⚪ Suspendida"
    }
    estado_actual = st.session_state["tracker"].log.get("node_states", {}).get(
        st.session_state["node_selected"], {}
    ).get("state", "Abierta")
    nuevo_estado = st.radio(
        "Selecciona el estado actual de esta subpregunta:",
        list(estados.keys()),
        index=list(estados.keys()).index(estado_actual) if estado_actual in estados else 0,
        format_func=lambda x: estados[x]
    )
    if st.button("Actualizar estado epistémico"):
        st.session_state["tracker"].set_node_state(st.session_state["node_selected"], nuevo_estado)
        st.success(f"Estado actualizado a: {estados[nuevo_estado]}")

    st.subheader("Justifica tu selección antes de continuar")
    justificacion = st.text_area("Explica por qué esta subpregunta es clave para la indagación:")
    if st.button("Guardar justificación y avanzar"):
        st.session_state["tracker"].log_event(
            "justificacion",
            justificacion,
            marco=marco,
            parent_node=st.session_state["node_selected"]
        )
        st.success("Justificación registrada. Puedes avanzar.")

    st.subheader("Feedback plural (pares/docente) sobre esta subpregunta")
    comment_text = st.text_area("Deja aquí tu comentario sobre la subpregunta, respuesta o reflexión del usuario:", key="comment_text")
    comment_author = st.text_input("Tu nombre o alias:", key="comment_author")
    tipo = st.radio("Tipo de feedback:", ("Humano (pares/docente)", "IA"), key="tipo_feedback")
    if st.button("Añadir comentario"):
        st.session_state["tracker"].add_feedback(
            st.session_state["node_selected"],
            comment_text,
            author=comment_author if comment_author else "Anónimo",
            tipo=tipo
        )
        st.success("¡Comentario añadido!")

    feedbacks = st.session_state["tracker"].log.get("feedback", {}).get(st.session_state["node_selected"], [])
    if feedbacks:
        st.markdown("#### Comentarios recibidos:")
        for fb in feedbacks:
            st.markdown(f"- _{fb['author']} ({fb['tipo']}):_ {fb['comment']}")
    else:
        st.info("Aún no hay comentarios en esta subpregunta.")

# ---- 9. Generar y comparar respuestas multiperspectiva ----
def generar_respuestas_multiperspectiva(nodo, marco, chat_fn):
    prompt = (
        f"Analiza la siguiente cuestión desde tres perspectivas.\n"
        f"Subpregunta: “{nodo}”\n"
        f"Marco seleccionado: {marco}\n"
        "Proporciona tres respuestas bien argumentadas y diferenciadas:\n"
        "1. Perspectiva ética (deontología, utilitarismo, ética del cuidado).\n"
        "2. Perspectiva histórico-sociopolítica relevante.\n"
        "3. Perspectiva crítica epistemológica o filosófica.\n"
        "Responde solo en JSON:\n"
        '[{"label": "Ética", "text": "..."}, {"label": "Histórico-Social", "text": "..."}, {"label": "Epistemológica", "text": "..."}]'
    )
    r = chat_fn([{"role": "system", "content": prompt}], max_tokens=700)
    try:
        data = json.loads(r.choices[0].message.content)
    except Exception:
        data = []
    return data

if "node_selected" in st.session_state:
    st.subheader("Genera y compara respuestas multiperspectiva")
    if st.button("Obtener respuestas multiperspectiva"):
        respuestas = generar_respuestas_multiperspectiva(
            st.session_state["node_selected"], marco, chat
        )
        st.session_state["respuestas_multiperspectiva"] = respuestas
        st.session_state["tracker"].log_event(
            "respuestas_multiperspectiva",
            respuestas,
            marco=marco,
            parent_node=st.session_state["node_selected"]
        )

if "respuestas_multiperspectiva" in st.session_state:
    st.markdown("### Respuestas contrastadas para la subpregunta seleccionada:")
    for item in st.session_state["respuestas_multiperspectiva"]:
        st.markdown(f"**{item['label']}**: {item['text']}")
    st.info("Reflexiona y compara las respuestas antes de continuar.")

    seleccion_usuario = st.radio(
        "¿Cuál perspectiva te parece más fundamentada/interesante para este caso?",
        [r["label"] for r in st.session_state["respuestas_multiperspectiva"]],
        index=0,
        key="seleccion_perspectiva"
    )
    justificacion_usuario = st.text_area(
        "¿Por qué escoges esa perspectiva como la más relevante aquí? ¿Cambiaría algo si eligieras otra?",
        key="justificacion_perspectiva"
    )
    if st.button("Registrar elección y reflexión"):
        st.session_state["tracker"].log_event(
            "eleccion_perspectiva",
            {
                "perspectiva": seleccion_usuario,
                "justificacion": justificacion_usuario
            },
            marco=marco,
            parent_node=st.session_state["node_selected"]
        )
        st.success("Elección y reflexión registradas.")

# ---- 10. Exportación y visualización de Reasoning Tracker ----
st.header("3. Exporta y revisa tu proceso deliberativo")
razonamiento = st.session_state["tracker"].export()
st.download_button("Descargar razonamiento (JSON)", razonamiento, file_name="razonamiento.json")

import io
if st.button("Descargar informe deliberativo en HTML"):
    html_content = generate_html_report(st.session_state["tracker"].log)
    st.download_button("Descargar informe (HTML)", data=html_content, file_name="informe_deliberativo.html", mime="text/html")

if st.checkbox("Ver historial de razonamiento"):
    st.json(st.session_state["tracker"].log)

st.info("Versión en construcción: ahora con estados epistémicos, feedback plural, colores y emojis en el árbol deliberativo.")

