# modules/contextual_generator.py

import os
import json
import openai

# Configura tu clave de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_responses(tree: dict, mode: str) -> dict:
    """
    Recorre el árbol de indagación y genera respuestas desde
    tres marcos teóricos: ética, histórica y crítica.
    """
    responses = {}

    def recurse(node):
        prompt = f"""
Eres un Generador Contextual de IA deliberativa.
Nodo: '{node['node']}'
Modo de usuario: {mode}

Proporciona tres respuestas argumentadas:
1. Perspectiva ética.
2. Perspectiva histórica.
3. Perspectiva crítica.

Responde **solo** en formato JSON así:

{{
  "node": "{node['node']}",
  "responses": [
    {{"label": "Ética", "text": "..."}},
    {{"label": "Histórica", "text": "..."}},
    {{"label": "Crítica", "text": "..."}}
  ]
}}
"""
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        try:
            data = json.loads(resp.choices[0].message.content)
        except json.JSONDecodeError:
            data = {"responses": []}
        responses[node["node"]] = data.get("responses", [])
        for child in node.get("children", []):
            recurse(child)

    recurse(tree[0])
    return responses
