import networkx as nx
from pyvis.network import Network

def render(G, height=600, width=800, relabel=False, **params):
    net = Network(height=height, width=width, directed=True, **params)
    if isinstance(G, str):
        net.from_DOT(G)
        return net
    if relabel:
        #mapping = {n: n.name for n in G}
        mapping = {n: G.nodes._nodes[n]['_id'] for n in G}
        net.from_nx(nx.relabel_nodes(G, mapping))
    else:
        net.from_nx(G)
    return net

def show(G, output='graph.html', relabel=True):
    net = render(G, relabel=relabel, notebook=False)
    net.show(output)
