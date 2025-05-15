# modules/html_exporter.py
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

def generate_html_report(reasoning_log):
    root = None
    if reasoning_log["inquiry"]:
        root = reasoning_log["inquiry"][0] if isinstance(reasoning_log["inquiry"], list) else reasoning_log["inquiry"]
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
      <p>{reasoning_log['root']}</p>
    </div>
    <div class='block'>
      <h2>2. Árbol de Subpreguntas ({len(reasoning_log.get('inquiry',[]))})</h2>
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
        # Recorte/resumen inteligente para que no se rompa visualmente
        cont = step.get('content','')
        if isinstance(cont, dict):
            cont = json.dumps(cont, ensure_ascii=False)
        elif isinstance(cont, list):
            cont = "; ".join(str(x) for x in cont)
        html += f"<td>{cont[:400]}{'...' if len(str(cont)) > 400 else ''}</td>"
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

    html += "<hr/><p style='color:#888'>Generado automáticamente con Código Deliberativo IA</p>"
    html += "</body></html>"
    return html
