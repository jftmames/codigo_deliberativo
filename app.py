# app.py

import os
import json
import streamlit as st
import openai

# 0. Configuración de página
st.set_page_config(
    page_title="Código Deliberativo Educativo",
    page_icon="🧠",
    layout="wide"
)

# 1. Barra lateral – Introducción y ajustes
st.sidebar.header("🔧 Ajustes")
st.sidebar.markdown(
    """
    **Perfil**  
    Elige tu nivel de profundidad y guiado en la indagación.
    """
)
mode = st.sidebar.selectbox(
    "Perfil del usuario",
    ["Asistido (básico)", "Guiado (intermedio)", "Exploratorio (avanzado)"]
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **API Key**  
    Asegúrate de haber configurado tu variable de entorno  
    `OPENAI_API_KEY` antes de desplegar.
    """,
    help="Se usa para autenticar con OpenAI."
)

# 2. Título principal
st.title("🧠 Código Deliberativo para Pensamiento Crítico")
st.markdown(
    """
    Esta aplicación te guía paso a paso para **estructurar**, **explorar** y **evaluar**
    procesos de indagación críticos, usando un modelo de IA deliberativa.
    """
)

# 3. Entrada de la pregunta
root_question = st.text_input(
    "1. Pregunta raíz",
    placeholder="Ej. ¿Es ético el uso de IA en diagnósticos médicos?",
    help="Formula aquí el tema o problema que quieres explorar."
)
if not root_question:
    st.warning("Por favor, escribe una *pregunta raíz* para continuar.")
    st.stop()

# Prepara OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
def chat(messages, max_tokens=500):
    return openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=max_tokens,
    )

# —————————————————————————————————————————
# 4. Paso 1: Generar árbol de indagación
# —————————————————————————————————————————
st.header("2. Generación de Subpreguntas 🔍")
with st.spinner("Creando árbol de indagación…"):
    inquiry_prompt = (
        "Eres un generador de subpreguntas para fomentar el pensamiento crítico.\n"
        f"Pregunta raíz: “{root_question}”\n"
        f"Perfil: {mode}\n\n"
        "1. Identifica 3–5 subpreguntas relevantes.\n"
        "2. Organízalas en una estructura jerárquica.\n"
        "Responde solo con JSON:\n"
        '{ "node": "…", "children": [ … ] }'
    )
    resp1 = chat([{"role": "system", "content": inquiry_prompt}], max_tokens=600)
    try:
        inquiry_tree = json.loads(resp1.choices[0].message.content)
    except Exception:
        st.error("❌ No se pudo interpretar la respuesta del modelo.")
        st.stop()

# Renderiza con Graphviz
st.subheader("Árbol de Indagación")
def build_dot(node):
    edges = ""
    label = node.get("node", "<sin etiqueta>")
    for child in node.get("children", []):
        c_label = child.get("node", "<sin etiqueta>")
        edges += f"\"{label}\" -> \"{c_label}\";\n"
        edges += build_dot(child)
    return edges

root = inquiry_tree[0] if isinstance(inquiry_tree, list) else inquiry_tree
dot = f"digraph G {{\n{build_dot(root)}}}"
st.graphviz_chart(dot, use_container_width=True)

# —————————————————————————————————————————
# 5. Paso 2: Generar respuestas argumentadas
# —————————————————————————————————————————
st.header("3. Respuestas Contextualizadas 💬")
responses = {}

def recurse_responses(node):
    prompt = (
        "Eres un Generador Contextual de IA deliberativa.\n"
        f"Nodo: “{node['node']}”\nPerfil: {mode}\n\n"
        "Proporciona tres respuestas:\n"
        "1. Perspectiva ética.\n"
        "2. Perspectiva histórica.\n"
        "3. Perspectiva crítica.\n\n"
        "Responde solo con JSON:\n"
        '{"node":"...","responses":[{"label":"Ética","text":"..."},...]}'
    )
    r = chat([{"role": "system", "content": prompt}], max_tokens=800)
    try:
        data = json.loads(r.choices[0].message.content)
    except Exception:
        data = {"responses": []}
    responses[node["node"]] = data.get("responses", [])
    for c in node.get("children", []):
        recurse_responses(c)

with st.spinner("Generando respuestas…"):
    recurse_responses(root)

# Mostrar
for node, resp_list in responses.items():
    st.markdown(f"**{node}**")
    for item in resp_list:
        st.write(f"- **{item['label']}**: {item['text']}")

# —————————————————————————————————————————
# 6. Paso 3: Sugerencias de reformulación
# —————————————————————————————————————————
st.header("4. Reformulación de Foco 🔄")
focus_suggestions = []
with st.spinner("Analizando reformulaciones…"):
    prompt2 = (
        "Eres un Motor de Diálogo Adaptativo.\n"
        f"Árbol (JSON): {json.dumps(inquiry_tree, ensure_ascii=False)}\n"
        f"Perfil: {mode}\n\n"
        "Si hay ambigüedad, sugiere hasta 2 reformulaciones de la pregunta.\n"
        "Responde solo con JSON de lista:\n"
        '[{"original":"…","suggestions":["…","…"]},…]'
    )
    r2 = chat([{"role": "system", "content": prompt2}], max_tokens=300)
    try:
        focus_suggestions = json.loads(r2.choices[0].message.content)
    except Exception:
        focus_suggestions = []

if focus_suggestions:
    for s in focus_suggestions:
        st.info(f"> **Original:** {s.get('original')}")
        for sug in s.get("suggestions", []):
            st.write(f"- {sug}")
else:
    st.success("No se necesitan reformulaciones.")

# —————————————————————————————————————————
# 7. Paso 4: EEE y descarga
# —————————————————————————————————————————
st.header("5. Índice de Equilibrio Erotético (EEE) & Informe 📥")
# Construye el log
log = {
    "root": root_question,
    "inquiry": inquiry_tree,
    "responses": responses,
    "focus": focus_suggestions,
}

# Calcula EEE
def calc_eee(root_node, responses, focus):
    def depth(n):
        return 1 + max((depth(c) for c in n.get("children", [])), default=0)
    prof = depth(root_node)
    avg_resp = sum(len(v) for v in responses.values()) / max(len(responses),1)
    rev = len(focus)
    d = min(prof/5,1)
    p = min(avg_resp/3,1)
    r = min(rev/2,1)
    return round((d+p+r)/3, 2)

eee = calc_eee(root, responses, focus_suggestions)
st.metric("EEE", f"{eee} / 1.00")

# Botón de descarga
st.download_button(
    label="⬇️ Descargar informe",
    data=json.dumps(log, ensure_ascii=False, indent=2),
    file_name="informe_deliberativo.json",
    mime="application/json"
)

# 🎉 Celebración
st.balloons()
