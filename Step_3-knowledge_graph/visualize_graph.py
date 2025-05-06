# visualize_graph.py

from rdflib import Graph
import networkx as nx
import matplotlib.pyplot as plt

def visualize_kg(filepath="knowledge_graph.ttl"):
    g = Graph()
    g.parse(filepath, format="turtle")
    nxg = nx.DiGraph()
    for s, p, o in g:
        nxg.add_edge(str(s).split('/')[-1], str(o), label=str(p).split('/')[-1])
    pos = nx.spring_layout(nxg, seed=42)
    labels = nx.get_edge_attributes(nxg, 'label')
    plt.figure(figsize=(14, 10))
    nx.draw(nxg, pos, with_labels=True, node_size=3000, node_color="skyblue", edge_color="gray", font_size=8)
    nx.draw_networkx_edge_labels(nxg, pos, edge_labels=labels, font_size=7)
    plt.title("Knowledge Graph Visualization")
    plt.show()

if __name__ == "__main__":
    visualize_kg("knowledge_graph.ttl")

