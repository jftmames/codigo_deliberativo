# modules/epistemic_navigator.py

import streamlit as st

def visualize_tree(tree):
    """
    Dibuja el árbol de indagación usando Graphviz de Streamlit.
    Admite tanto dict como lista de dicts.
    """
    # Determinar el nodo raíz
    if isinstance(tree, list) and len(tree) > 0:
        root = tree[0]
    elif isinstance(tree, dict):
        root = tree
    else:
        st.error("Formato de árbol de indagación inválido.")
        return

    def build_dot(node):
        edges = ""
        # Cada nodo debe tener la clave "node" y opcionalmente "children"
        node_label = node.get("node", "<unknown>")
        for child in node.get("children", []):
            child_label = child.get("node", "<unknown>")
            edges += f"\"{node_label}\" -> \"{child_label}\";\n"
            edges += build_dot(child)
        return edges

    dot_body = build_dot(root)
    dot = f"digraph G {{\n{dot_body}}}"
    st.graphviz_chart(dot)
