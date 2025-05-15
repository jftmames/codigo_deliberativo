import json

def render_html_tree(node):
    if node is None:
        return ""
    html = f"<li><strong>{node.get('node','')}</strong>"
    children = node.get("children", [])
    if children:
        html += "<ul>"
        for c in children:
            html += render_html_tree(c)
        html += "</ul>"
    html += "</li>"
    return html

def generate_html_report(reasoning_log):
    inquiry = reasoning_log.get('inquiry', None)
    if inquiry:
        root = inquiry[0] if isinstance(inquiry, list) else inquiry
    else:
        root = {"node": "<sin árbol>", "children": []}

    html = f"""
    <html>
    <head>
    <meta charset='utf-8'/>
    <title>Informe Deliberativo</title>
    <style>
      body {{
        font-family: 'Segoe UI', sans-serif; color: #222; background: #fff; padding: 2em;
      }}
      h1, h2, h3 {{ color: #113356; }}
      ul {{ margin-left: 2em; }}
      li {{ margin-bottom: 0.6em; }}
      .block {{ margin-bottom: 2em; }}
      .step-table {{ border-collapse: collapse; width: 98%; }}
      .step-table th, .step-table td {{ border: 1px solid #bbb; padding: 7px 12px; text-align: left; }}
      .step-table th {{ background: #e5e9f5; }}
    </style>
    </head>
    <body>
    <h1>Informe Deliberativo - Pensamiento Crítico</h1>

    <div class='block'>
      <h2>1. Pregunta Raíz</h2>
      <p>{reasoning_log.get('root', '')}</p>
    </div>
    <div class='block'>
      <h2>2. Árbol de Subpreguntas</h2>
      <ul>
      {render_html_tree(root)}
      </ul>
    </div>
    <div class='block'>
      <h2>3. Pasos, Selecciones y Justificaciones</h2>
      <table class='step-table'>
        <tr>
          <th>Momento</th>
          <th>Tipo de Acción</th>
          <th>Contenido / Resumen</th>
          <th>Marco</th>
          <th>Subpregunta/Nodo</th>
        </tr>
    """
    for step in reasoning_log.get("steps", []):
        html += "<tr>"
        html += f"<td>{step.get('timestamp','')}</td>"
        html += f"<td>{step.get('event_type','')}</td>"
        cont = step.get('content','')
        if isinstance(cont, dict):
            cont = json.dumps(cont, ensure_ascii=False)
        elif isinstance(cont, list):
            cont = "; ".join(str(x) for x in cont)
        html += f"<td>{str(cont)[:400]}{'...' if len(str(cont)) > 400 else ''}</td>"
        html += f"<td>{step.get('marco','')}</td>"
        html += f"<td>{step.get('parent_node','')}</td>"
        html += "</tr>"
    html += "</table></div>"

    html += "<div class='block'><h2>4. Respuestas Multiperspectiva Registradas</h2>"
    respuestas = reasoning_log.get("responses", {})
    if respuestas:
        for nodo, resp_list in respuestas.items():
            html += f"<strong>{nodo}</strong><ul>"
            for r in resp_list:
                html += f"<li><b>{r.get('label','')}</b>: {r.get('text','')}</li>"
            html += "</ul>"
    else:
        html += "<p>No se registraron respuestas.</p>"
    html += "</div>"

    html += "<div class='block'><h2>5. Foco/Evolución (si aplica)</h2><ul>"
    for foco in reasoning_log.get("focus", []):
        html += f"<li>{foco}</li>"
    html += "</ul></div>"

    html += "<div class='block'><h2>6. Feedback plural recibido</h2>"
    feedback = reasoning_log.get("feedback", {})
    if feedback:
        for nodo, comentarios in feedback.items():
            html += f"<strong>{nodo}</strong><ul>"
            for fb in comentarios:
                html += f"<li><b>{fb.get('author','Anónimo')} ({fb.get('tipo','')})</b>: {fb.get('comment','')}</li>"
            html += "</ul>"
    else:
        html += "<p>No se registraron comentarios.</p>"
    html += "</div>"

    html += "<div class='block'><h2>7. Estado epistémico de cada subpregunta</h2><ul>"
    node_states = reasoning_log.get("node_states", {})
    for node, data in node_states.items():
        html += f"<li><b>{node}</b>: {data['state']} (actualizado: {data['timestamp']})</li>"
    html += "</ul></div>"

    html += "<hr/><p style='color:#888'>Generado automáticamente con Código Deliberativo IA</p>"
    html += "</body></html>"
    return html
