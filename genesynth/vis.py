from pyvis.network import Network

def render(G, output='graph.html', **params):
    net = Network(directed=True, **params)
    mapping = {n: n.name for n in G}
    net.from_nx(nx.relabel_nodes(G, mapping))
    net.show(output)


