# modules/epistemic_navigator.py

import streamlit as st
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout

def visualize_tree(tree: dict):
    """
    Dibuja el árbol de indagación usando NetworkX y Graphviz,
    y lo muestra en Streamlit.
    """
    G = nx.DiGraph()

    def add_nodes_edges(node):
        G.add_node(node["node"])
        for child in node.get("children", []):
            G.add_node(child["node"])
            G.add_edge(node["node"], child["node"])
            add_nodes_edges(child)

    # Asumimos que `tree` es una lista con un único elemento raíz
    add_nodes_edges(tree[0])

    pos = graphviz_layout(G, prog="dot")
    # Dibujamos sobre matplotlib
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, arrows=True, ax=ax)
    st.pyplot(fig)
