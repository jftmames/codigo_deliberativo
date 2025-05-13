# modules/inquiry_engine.py

from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

# Plantilla base para generar subpreguntas jerárquicas
INQUIRY_PROMPT = PromptTemplate(
    input_variables=["question", "mode"],
    template="""
Eres un generador de subpreguntas para fomentar el pensamiento crítico.
Pregunta raíz: "{question}"
Nivel de usuario: {mode}

1. Identifica 3–5 subpreguntas relevantes que amplíen, profundicen o diversifiquen el análisis.
2. Organízalas jerárquicamente (pregunta → subpregunta).
3. Devuelve el resultado en formato JSON:
[
  {{ "node": "Pregunta Raíz", "children": [ ... ] }}
]
"""
)

_llm = OpenAI(temperature=0.7, max_tokens=500)

def generate_inquiry_tree(root_question: str, mode: str) -> dict:
    """
    Llama a un LLM para generar un árbol JSON de indagación
    según la pregunta raíz y el modo de usuario.
    """
    chain = LLMChain(llm=_llm, prompt=INQUIRY_PROMPT)
    result = chain.run(question=root_question, mode=mode)
    # Suponemos que `result` es un JSON serializado
    import json
    tree = json.loads(result)
    return tree
