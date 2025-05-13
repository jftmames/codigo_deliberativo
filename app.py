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
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": INQUIRY_PROMPT.format(question=root_question, mode=mode)}
        ],
        temperature=0.7,
        max_tokens=500,
    )
    content = response.choices[0].message.content
    return json.loads(content)


