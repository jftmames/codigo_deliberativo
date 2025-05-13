# app.py

import streamlit as st
from modules.inquiry_engine import generate_inquiry_tree
from modules.contextual_generator import generate_responses
from modules.epistemic_navigator import visualize_tree
from modules.adaptive_dialogue import adapt_focus
from modules.reasoning_tracker import ReasoningTracker
from modules.eee_evaluator import calculate_eee

# --- Configuración de la página ---
st.set_page_config(page_title="Tutor Deliberativo", layout="wide")
st.title("🔍 Tutor IA Deliberativo: Potenciador de Pensamiento Crítico")

# --- Barra lateral: perfil de usuario ---
st.sidebar.header("Configuración del Perfil")
mode = st.sidebar.radio(
    "Selecciona tu nivel de profundización:",
    ["Modo asistido", "Modo guiado", "Modo exploratorio"]
)

# --- Entrada de la pregunta raíz ---
st.markdown("### 1. Introduce tu pregunta para iniciar la indagación crítica:")
root_question = st.text_input("Pregunta raíz", key="root_question")

# --- Proceso deliberativo ---
if root_question:
    # Inicializar tracker
    if "tracker" not in st.session_state:
        st.session_state["tracker"] = ReasoningTracker(root_question)

    tracker = st.session_state["tracker"]

    # 1. Generar árbol de indagación
    inquiry_tree = generate_inquiry_tree(root_question, mode)
    tracker.log_inquiry(inquiry_tree)

    # 2. Visualizar trayectorias epistémicas
    st.markdown("### 2. Navegación de trayectorias de indagación")
    visualize_tree(inquiry_tree)

    # 3. Generar respuestas desde múltiples marcos
    st.markdown("### 3. Respuestas argumentadas por nodo")
    responses = generate_responses(inquiry_tree, mode)
    tracker.log_responses(responses)
    for node, resp_list in responses.items():
        st.write(f"**{node}**")
        for resp in resp_list:
            st.markdown(f"> *{resp['label']}*: {resp['text']} ")

    # 4. Sugerir reformulación de foco si procede
    st.markdown("### 4. Sugerencias de reformulación del foco")
    suggestions = adapt_focus(inquiry_tree, mode)
    if suggestions:
        tracker.log_focus_change(suggestions)
        for item in suggestions:
            st.markdown(f"- **{item['original']}** → {', '.join(item['suggestions'])}")
    else:
        st.info("No se sugerieron reformulaciones adicionales.")

    # 5. Evaluación con EEE
    st.markdown("### 5. Índice de Equilibrio Erotético (EEE)")
    eee_score = calculate_eee(tracker)
    st.metric(label="EEE Score", value=f"{eee_score:.2f}")

    # 6. Exportar informe deliberativo
    st.markdown("### 6. Exportar proceso deliberativo")
    report = tracker.export()
    st.download_button(
        label="Descargar informe (JSON)",
        data=report,
        file_name="informe_deliberativo.json",
        mime="application/json"
    )

# modules/inquiry_engine.py

import openai
import os
import json

# Configurar API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Plantilla para generar subpreguntas jerárquicas
INQUIRY_PROMPT = '''
Eres un generador de subpreguntas para fomentar el pensamiento crítico.
Pregunta raíz: '{question}'
Nivel de usuario: {mode}

1. Identifica 3–5 subpreguntas relevantes.
2. Organízalas jerárquicamente.
Responde en formato JSON.
'''

def generate_inquiry_tree(root_question: str, mode: str) -> dict:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": INQUIRY_PROMPT.format(question=root_question, mode=mode)}
        ],
        temperature=0.7,
        max_tokens=500,
    )
    content = response.choices[0].message.content
    return json.loads(content)

# modules/epistemic_navigator.py

import streamlit as st
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt

def visualize_tree(tree: dict):
    G = nx.DiGraph()
    def add_edges(node):
        G.add_node(node["node"])
        for child in node.get("children", []):
            G.add_node(child["node"])
            G.add_edge(node["node"], child["node"])
            add_edges(child)
    add_edges(tree[0])
    pos = graphviz_layout(G, prog="dot")
    fig, ax = plt.subplots(figsize=(8,6))
    nx.draw(G, pos, with_labels=True, arrows=True, ax=ax)
    st.pyplot(fig)

# modules/contextual_generator.py

import os
import json
import openai

# Configurar clave API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt para generar respuestas desde múltiples marcos teóricos
CONTEXTUAL_PROMPT = '''
Eres un Generador Contextual de IA deliberativa.
Nodo: '{node}'
Modo: {mode}

Proporciona **tres** respuestas argumentadas:
1. Perspectiva ética.
2. Perspectiva histórica.
3. Perspectiva crítica.

Responde **solo** en formato JSON:
{
  "node": "{node}",
  "responses": [
    {"label": "Ética", "text": "..."},
    {"label": "Histórica", "text": "..."},
    {"label": "Crítica", "text": "..."}
  ]
}
'''

def generate_responses(tree: dict, mode: str) -> dict:
    responses = {}
    def recurse(node):
        prompt = CONTEXTUAL_PROMPT.format(node=node["node"], mode=mode)
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        data = json.loads(resp.choices[0].message.content)
        responses[node["node"]] = data.get("responses", [])
        for child in node.get("children", []):
            recurse(child)
    recurse(tree[0])
    return responses

# modules/adaptive_dialogue.py

# (removed langchain dependency)
# (removed langchain dependency)
import json

ADAPTIVE_PROMPT = PromptTemplate(
    input_variables=["tree_json","mode"],
    template="""
Eres Motor de Diálogo Adaptativo.
Árbol: {tree_json}
Modo: {mode}

1. Identifica ambigüedades.
2. Sugiere hasta 2 reformulaciones.
3. Devuelve JSON [{{'original':'', 'suggestions':['','']}}]
"""
)

_llm = OpenAI(temperature=0.7, max_tokens=300)

def adapt_focus(tree: dict, mode: str) -> list:
    return json.loads(_llm(ADAPTIVE_PROMPT.format(tree_json=json.dumps(tree), mode=mode)))

# modules/reasoning_tracker.py

import json
from datetime import datetime

class ReasoningTracker:
    def __init__(self, root_question):
        self.log = {"root":root_question, "inquiry":None, "responses":{}, "focus":[], "times":[]}
    def log_inquiry(self, tree): self.log.update({"inquiry":tree}); self._stamp('inquiry')
    def log_responses(self, resp): self.log.update({"responses":resp}); self._stamp('responses')
    def log_focus_change(self, s): self.log['focus'].append(s); self._stamp('focus')
    def _stamp(self,evt): self.log['times'].append({evt:datetime.utcnow().isoformat()})
    def export(self): return json.dumps(self.log, ensure_ascii=False, indent=2)

# modules/eee_evaluator.py

import json
from statistics import mean

def calculate_eee(tracker):
    log = json.loads(tracker.export())
    tree = log.get('inquiry',[])
    depth = lambda n: 1+max([depth(c) for c in n.get('children',[])], default=0)
    prof = depth(tree[0]) if tree else 0
    resp_counts = [len(v) for v in log.get('responses',{}).values()]
    plural = mean(resp_counts) if resp_counts else 0
    rev = len(log.get('focus',[]))
    d_norm, p_norm, r_norm = min(prof/5,1), min(plural/3,1), min(rev/2,1)
    return mean([d_norm,p_norm,r_norm])


