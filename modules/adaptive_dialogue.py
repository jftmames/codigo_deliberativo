# modules/adaptive_dialogue.py

from langchain import PromptTemplate, LLMChain
from langchain.llms import OpenAI

# Plantilla para sugerir reformulación del foco de indagación
ADAPTIVE_PROMPT = PromptTemplate(
    input_variables=["tree_json", "mode"],
    template="""
Eres un Motor de Diálogo Adaptativo para IA deliberativa.
Has procesado el siguiente árbol de indagación (JSON):
{tree_json}

Modo de usuario: {mode}

1. Identifica si hay nodos con alto grado de ambigüedad o falta de profundización.
2. Si es necesario, sugiere hasta dos reformulaciones de la pregunta raíz o de subpreguntas,
   para profundizar o clarificar el análisis.
3. Devuelve un JSON:
[
  {{ "original": "Pregunta original o nodo", "suggestions": ["Reformulación 1", "Reformulación 2"] }}
]
Si no hay sugerencias, devuelve [].
"""
)

_llm = OpenAI(temperature=0.7, max_tokens=300)

def adapt_focus(tree: dict, mode: str) -> list:
    """
    Analiza el árbol y sugiere reformulaciones de foco.
    """
    import json
    chain = LLMChain(llm=_llm, prompt=ADAPTIVE_PROMPT)
    tree_json = json.dumps(tree, ensure_ascii=False)
    result = chain.run(tree_json=tree_json, mode=mode)
    suggestions = json.loads(result)
    return suggestions
