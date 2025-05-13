# modules/contextual_generator.py

from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

# Plantilla base para generar respuestas desde múltiples marcos teóricos
CONTEXTUAL_PROMPT = PromptTemplate(
    input_variables=["node", "mode"],
    template="""
Eres un Generador Contextual de IA deliberativa.
Nodo de indagación: "{node}"
Modo de usuario: {mode}

Para esta pregunta, proporciona **tres** respuestas argumentadas desde marcos distintos:
1. Una perspectiva ética (p. ej., deontológica o utilitarista).
2. Una perspectiva histórica o contextual.
3. Una perspectiva crítica o alternativa.

Devuelve un JSON con formato:
{{
  "node": "{node}",
  "responses": [
    {{ "label": "Ética", "text": "..." }},
    {{ "label": "Histórica", "text": "..." }},
    {{ "label": "Crítica", "text": "..." }}
  ]
}}
"""
)

_llm = OpenAI(temperature=0.7, max_tokens=600)

def generate_responses(tree: dict, mode: str) -> dict:
    """
    Recorre cada nodo del árbol y genera un bloque de respuestas
    contextualizadas. Devuelve un dict { nodo: [resp,...], ... }.
    """
    chain = LLMChain(llm=_llm, prompt=CONTEXTUAL_PROMPT)
    import json

    responses = {}
    def recurse(node):
        result = chain.run(node=node["node"], mode=mode)
        data = json.loads(result)
        responses[node["node"]] = data["responses"]
        for child in node.get("children", []):
            recurse(child)

    # Asumimos lista con raíz
    recurse(tree[0])
    return responses
