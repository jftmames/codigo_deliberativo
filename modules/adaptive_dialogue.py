# modules/adaptive_dialogue.py

import os
import json
import openai

# Configura tu clave de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def adapt_focus(tree: dict, mode: str) -> list:
    """
    Analiza el árbol de indagación y sugiere hasta dos reformulaciones
    si detecta ambigüedad o falta de profundidad.
    """
    prompt = f"""
Eres un Motor de Diálogo Adaptativo para IA deliberativa.
Árbol de indagación (JSON):
{json.dumps(tree, ensure_ascii=False)}

Modo de usuario: {mode}

1. Identifica si hay nodos con alto grado de ambigüedad o poca profundización.
2. Sugiere hasta **dos** reformulaciones de la pregunta raíz o de alguna subpregunta.
3. Devuelve tu respuesta **solo** en formato JSON así:

[
  {{
    "original": "Texto de la pregunta original",
    "suggestions": ["Reformulación 1", "Reformulación 2"]
  }}
]

Si no hay nada que sugerir, devuelve [].
"""
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    try:
        suggestions = json.loads(resp.choices[0].message.content)
    except json.JSONDecodeError:
        suggestions = []
    return suggestions
