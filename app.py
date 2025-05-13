# app.py

import os
import json
import streamlit as st
import openai

# 0. Configuración
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="Código Deliberativo Educativo", layout="wide")

st.title("🧠 Código Deliberativo para Pensamiento Crítico")

# 1. Inputs: pregunta raíz y modo
mode = st.sidebar.selectbox(
    "Elige tu perfil",
    ["asistido (básico)", "guiado (intermedio)", "exploratorio (avanzado)"],
)
root_question = st.text_input("1. Escribe tu pregunta raíz:", "")

if not root_question:
    st.info("Introduce una pregunta para comenzar.")
    st.stop()

# Helper: llamada al modelo
def chat(messages, max_tokens=500):
    return openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=max_tokens,
    )

# 2. Inquiry Engine
with st.spinner("Generando árbol de indagación…"):
    inquiry_prompt = (
        "Eres un generador de subpreguntas para fomentar el pensamiento crítico.\n"
        f"Pregunta raíz: '{root_question}'\n"
        f"Modo de usuario: {mode}\n\n"
        "1. Identifica 3–5 subpreguntas relevantes.\n"
        "2. Organízalas jerárquicamente.\n"
        "Responde solo en JSON con estructura: { \"node\": ..., \"children\": [...] }"
    )
    resp = chat([{"role": "system", "content": inquiry_prompt}], max_tokens=600)
    try:
        inquiry_tree = json.loads(resp.choices[0].message.content)
    except Exception:
        st.error("Error al parsear el árbol de indagación.")
        st.stop()

# Visualizar con Graphviz
st.subheader("2. Árbol de Indagación")
def build_dot(node):
    edges = ""
    label = node.get("node", "<sin nodo>")
    for child in node.get("children", []):
        c_label = child.get("node", "<sin nodo>")
        edges += f"\"{label}\" -> \"{c_label}\";\n"
        edges += build_dot(child)
    return edges

# Aceptamos que root pueda ser lista o dict
root = inquiry_tree[0] if isinstance(inquiry_tree, list) else inquiry_tree
dot = f"digraph G {{\n{build_dot(root)}}}"
st.graphviz_chart(dot)

# 3. Contextual Generator
st.subheader("3. Respuestas Argumentadas")
responses = {}
def recurse_responses(node):
    prompt = (
        "Eres un Generador Contextual de IA deliberativa.\n"
        f"Nodo: '{node['node']}'\nModo: {mode}\n\n"
        "Proporciona tres respuestas argumentadas:\n"
        "1. Perspectiva ética.\n2. Perspectiva histórica.\n3. Perspectiva crítica.\n\n"
        "Responde solo en JSON: "
        "{\"node\":\"...\",\"responses\":[{\"label\":\"Ética\",\"text\":\"...\"},"
        "{\"label\":\"Histórica\",\"text\":\"...\"},"
        "{\"label\":\"Crítica\",\"text\":\"...\"}]}"
    )
    r = chat([{"role":"system","content":prompt}], max_tokens=800)
    try:
        data = json.loads(r.choices[0].message.content)
    except Exception:
        data = {"responses":[]}
    responses[node["node"]] = data.get("responses", [])
    for c in node.get("children", []):
        recurse_responses(c)

with st.spinner("Generando respuestas…"):
    recurse_responses(root)

for node, resp_list in responses.items():
    st.markdown(f"**{node}**")
    for item in resp_list:
        st.write(f"- *{item['label']}*: {item['text']}")

# 4. Adaptive Dialogue Engine
st.subheader("4. Sugerencias de Reformulación")
focus_suggestions = []
with st.spinner("Analizando posibles reformulaciones…"):
    prompt2 = (
        "Eres un Motor de Diálogo Adaptativo.\n"
        f"Árbol (JSON): {json.dumps(inquiry_tree, ensure_ascii=False)}\n"
        f"Modo: {mode}\n\n"
        "Si ves ambigüedad, sugiere hasta 2 reformulaciones de la pregunta raíz o subpreguntas.\n"
        "Devuelve solo un JSON de lista: "
        "[{\"original\":\"...\",\"suggestions\":[\"…\",\"…\"]}, ...]"
    )
    r2 = chat([{"role":"system","content":prompt2}], max_tokens=300)
    try:
        focus_suggestions = json.loads(r2.choices[0].message.content)
    except Exception:
        focus_suggestions = []

if focus_suggestions:
    for s in focus_suggestions:
        st.write(f"> **Original:** {s.get('original')}")
        for sug in s.get("suggestions", []):
            st.write(f"- {sug}")
else:
    st.write("No se sugieren reformulaciones.")

# 5. Reasoning Tracker & EEE
st.subheader("5. Métrica EEE y Exportación")
# Construimos un log simplificado
log = {
    "root": root_question,
    "inquiry": inquiry_tree,
    "responses": responses,
    "focus": focus_suggestions,
}

# EEE simple: profundidad, pluralidad y sugerencias
def calc_eee(log):
    # profundidad
    def depth(n):
        return 1 + max((depth(c) for c in n.get("children", [])), default=0)
    prof = depth(root)
    # pluralidad
    avg_resp = sum(len(v) for v in responses.values()) / max(len(responses),1)
    # reformulaciones
    rev = len(focus_suggestions)
    # normalizamos (suponiendo umbrales 5,3,2)
    d = min(prof/5,1)
    p = min(avg_resp/3,1)
    r = min(rev/2,1)
    return round((d+p+r)/3, 2)

eee = calc_eee(log)
st.metric("Índice de Equilibrio Erotético (EEE)", eee)

# Botón de descarga
st.download_button(
    "⬇️ Descargar informe JSON",
    data=json.dumps(log, ensure_ascii=False, indent=2),
    file_name="informe_deliberativo.json",
    mime="application/json"
)
