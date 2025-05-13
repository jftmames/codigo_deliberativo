import os
import json
import streamlit as st
import openai
import pandas as pd
import streamlit.components.v1 as components

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

# 3. Entrada de la pregunta con ejemplos por defecto
st.header("1. Define tu pregunta raíz")
example_questions = [
    "¿Es ético el uso de IA en diagnósticos médicos?",
    "¿Deberían las redes sociales regular cierto tipo de contenido?",
    "¿Cómo impacta la automatización en el mercado laboral juvenil?",
    "¿Es sostenible el modelo económico actual?",
    "¿Debe implementarse la renta básica universal?"
]
st.markdown("🔍 **Selecciona un ejemplo** o escribe tu propia pregunta:")
selected_example = st.selectbox("Ejemplos de preguntas", ["— Ninguno —"] + example_questions)
if selected_example != "— Ninguno —":
    root_question = selected_example
    st.markdown(f"**Pregunta seleccionada:** {root_question}")
else:
    root_question = st.text_input(
        "Escribe tu pregunta aquí",
        placeholder="Ej. ¿Es ético el uso de IA en diagnósticos médicos?",
        help="Puedes usar uno de los ejemplos o escribir la tuya."
    )
if not root_question:
    st.warning("🛈 Necesitamos una pregunta raíz para continuar.")
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

# 4. Paso 1: Generar árbol de indagación
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

# Expander con lista de subpreguntas
st.subheader("📋 Ver todas las subpreguntas")
with st.expander("Mostrar subpreguntas en formato de lista"):
    def render_list(node, indent=0):
        st.markdown(" " * indent * 2 + f"- **{node.get('node', '<sin título>')}**")
        for c in node.get("children", []):
            render_list(c, indent + 1)
    render_list(root)

# 5. Paso 2: Generar respuestas argumentadas
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
for node, resp_list in responses.items():
    st.markdown(f"**{node}**")
    for item in resp_list:
        st.write(f"- **{item['label']}**: {item['text']}")

# 6. Paso 3: Reformulación de foco
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

# 7. Paso 4: EEE y descarga
st.header("5. Índice de Equilibrio Erotético (EEE) & Informe 📥")
log = {
    "root": root_question,
    "inquiry": inquiry_tree,
    "responses": responses,
    "focus": focus_suggestions,
}
def calc_eee(root_node, responses, focus):
    def depth(n):
        return 1 + max((depth(c) for c in n.get("children", [])), default=0)
    prof = depth(root_node)
    avg_resp = sum(len(v) for v in responses.values()) / max(len(responses),1)
    rev = len(focus)
    d, p, r = min(prof/5,1), min(avg_resp/3,1), min(rev/2,1)
    return round((d+p+r)/3, 2)

eee = calc_eee(root, responses, focus_suggestions)
st.metric("EEE", f"{eee} / 1.00")

# Extras: modos de visualización y desglose
st.header("6. Modos de Visualización y Métricas Detalladas ⚙️")
view_mode = st.radio(
    "Modo de vista del árbol de indagación:",
    ("Grafo (predeterminado)", "Listado anidado")
)
if view_mode == "Listado anidado":
    st.subheader("Listado Anidado del Árbol")
    render_list(root)
else:
    st.subheader("Grafo de Indagación")
    st.graphviz_chart(dot, use_container_width=True)

def calc_eee_components(root_node, responses, focus):
    def depth(n):
        return 1 + max((depth(c) for c in n.get("children", [])), default=0)
    prof = depth(root_node)
    avg_resp = sum(len(v) for v in responses.values()) / max(len(responses),1)
    rev = len(focus)
    return {
        "Profundidad": round(min(prof/5,1),2),
        "Pluralidad": round(min(avg_resp/3,1),2),
        "Reversibilidad": round(min(rev/2,1),2)
    }

components = calc_eee_components(root, responses, focus_suggestions)
components["EEE"] = eee
st.subheader("Métricas de Calidad Epistémica")
st.table(components.items())
st.subheader("Gráfico de Componentes del EEE")
df = pd.DataFrame.from_dict(components, orient="index", columns=["Valor"]).drop("EEE")
st.bar_chart(df)
st.markdown(f"**Índice EEE global:** {eee} / 1.00")

# Botón de descarga
st.download_button(
    label="⬇️ Descargar informe",
    data=json.dumps(log, ensure_ascii=False, indent=2),
    file_name="informe_deliberativo.json",
    mime="application/json"
)

# 8. Informe detallado en HTML
st.header("📄 Informe Detallado (HTML)")
def render_html_tree(node):
    html = f"<li><strong>{node.get('node','')}</strong>"
    children = node.get("children", [])
    if children:
        html += "<ul>"
        for c in children:
            html += render_html_tree(c)
        html += "</ul>"
    html += "</li>"
    return html

def generate_html_report(log):
    raw = log["inquiry"]
    root_node = raw[0] if isinstance(raw, list) else raw
    tree_html = render_html_tree(root_node)
    comps = calc_eee_components(root_node, log["responses"], log["focus"])
    comps["EEE"] = eee

    html = f"""
    <style>
      .section {{ margin-bottom: 1.5em; }}
      .section h3 {{ color: #2E86AB; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }}
      .section ul {{ list-style-type: disc; margin-left: 1em; }}
      .responses {{ margin-left: 1em; }}
      .metric-table {{ border-collapse: collapse; width: 50%; }}
      .metric-table th, .metric-table td {{ border: 1px solid #ddd; padding: 8px; }}
      .metric-table th {{ background-color: #f2f2f2; }}
    </style>
    <div class="section">
      <h3>1. Pregunta Raíz</h3>
      <p>{log["root"]}</p>
    </div>
    <div class="section">
      <h3>2. Árbol de Indagación</h3>
      <ul>
        {tree_html}
      </ul>
    </div>
    <div class="section">
      <h3>3. Respuestas Contextualizadas</h3>
    """
    for nodo, resp_list in log["responses"].items():
        html += f'<div class="responses"><strong>{nodo}</strong><ul>'
        for r in resp_list:
            html += f'<li><em>{r["label"]}:</em> {r["text"]}</li>'
        html += "</ul></div>"
    html += """
    </div>
    <div class="section">
      <h3>4. Reformulaciones Sugeridas</h3>
    """
    if log["focus"]:
        html += "<ul>"
        for f in log["focus"]:
            html += f'<li><strong>{f["original"]}</strong><ul>'
            for s in f["suggestions"]:
                html += f"<li>{s}</li>"
            html += "</ul></li>"
        html += "</ul>"
    else:
        html += "<p>No se sugirieron reformulaciones.</p>"
    html += """
    </div>
    <div class="section">
      <h3>5. Métricas Epistémicas</h3>
      <table class="metric-table">
        <tr><th>Componente</th><th>Valor</th></tr>
    """
    for k, v in comps.items():
        html += f"<tr><td>{k}</td><td>{v}</td></tr>"
    html += """
      </table>
    </div>
    """
    return html

html_report = generate_html_report(log)
components.html(html_report, height=700, scrolling=True)

# 🎉 Celebración
st.balloons()
