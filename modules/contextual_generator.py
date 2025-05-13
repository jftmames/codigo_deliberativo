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

    # Detectar raíz del árbol
    if isinstance(tree, list) and tree:
        root = tree[0]
    elif isinstance(tree, dict):
        root = tree
    else:
        return responses

    def recurse(node):
        prompt = f\"\"\"\nEres un Generador Contextual de IA deliberativa.\nNodo: '{node['node']}'\nModo de usuario: {mode}\n\nProporciona tres respuestas argumentadas:\n1. Perspectiva ética.\n2. Perspectiva histórica.\n3. Perspectiva crítica.\n\nResponde **solo** en formato JSON así:\n\n{{\n  \"node\": \"{node['node']}\",\n  \"responses\": [\n    {{\"label\": \"Ética\", \"text\": \"...\"}},\n    {{\"label\": \"Histórica\", \"text\": \"...\"}},\n    {{\"label\": \"Crítica\", \"text\": \"...\"}}\n  ]\n}}\n\"\"\"\n           resp = openai.chat.completions.create(\n               model=\"gpt-3.5-turbo\",\n               messages=[{\"role\": \"system\", \"content\": prompt}],\n               temperature=0.7,\n               max_tokens=600\n           )\n           try:\n               data = json.loads(resp.choices[0].message.content)\n           except json.JSONDecodeError:\n               data = {\"responses\": []}\n           responses[node['node']] = data.get(\"responses\", [])\n           for child in node.get(\"children\", []):\n               recurse(child)\n\n       recurse(root)\n       return responses


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
