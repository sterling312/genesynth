from pyvis.network import Network

def render(G, output='graph.html', height=600, width=800, relabel=False, **params):
    net = Network(height=height, width=width, directed=True, **params)
    if relabel:
        mapping = {n: n.name for n in G}
        net.from_nx(nx.relabel_nodes(G, mapping))
    else:
        net.from_nx(G)
    net.show(output)


