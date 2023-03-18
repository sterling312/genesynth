"""
Graph is solely responsible for entity relationships and logical order of operations.
Note that this is not intended to optimize processing order of operatsions and optimization.
The graph is required to be able to evaluate the dependency in isolation; this means no business logic.
"""

import enum
import networkx as nx
from genesynth import utils

class Node(enum.Enum):
    unique = 1 # node contains no duplicated value
    notnull = 2 # node contains no empty value
    sorted = 3 # ordered value, incremental if numeric, sorted if other
    subset = 4 # node contains value within the set (between is just (a...b) eps R)

class Relationship(enum.Enum):
    child = 1 # node is a child of parent
    subset = 2 # node contains subset of copy of parent
    ordered = 3 # node contains value that are based on ordered index of the parent, aka positional identity
    identity = 4 # node contains exact copy of parent
    incremental = 5 # node contains increasing value as parent

def find_node(G, name):
    for n in G.nodes:
        if n.name == name:
            return n

def find_child_node(G, parent, child):
    node = find_node(G, parent)
    g = G.subgraph(nx.descendants(G, node))
    return find_node(g, child) 

class Graph:
    """
    Handles all things graph traversal.
    Mainly used to detect deepest child (leaf) node and generate node processing sequence.
    """
    def __init__(self, G, name: str, ref: str = None, **attr):
        self.G = G
        self.name = name
        self.attr = attr
        self.ref = ref

    def subgraph(self, nodes):
        return self.G.subgraph(nodes)

    @property
    def nodes(self):
        return self.G.nodes

    @property
    def edges(self):
        return self.G.edges

    @property
    def root(self):
        return {n for n in self.G.nodes if self.G.in_degree(n) == 0}

    @property
    def model_nodes(self):
        return {n for n, d in self.G.nodes(data=True) if not n.is_data}

    @property
    def data_nodes(self):
        return {n for n, d in self.G.nodes(data=True) if n.is_data}

    def filter(self, **attrs):
        return {n for n, d in self.G.nodes(data=True) if d.items() >= attrs.items()}

    @property
    def leaf(self):
        return {n for n in self.G.nodes if self.G.in_degree(n) == 1 and self.G.out_degree(n) == 0}

    def parents(self, node):
        return nx.ancestors(self.G, node)

    def children(self, node):
        return nx.descendants(self.G, node)

    def node_degree(self):
        return dict(self.G.in_degree())

    def node_depth(self):
        depth = {}
        for root in self.root:
            depth.update(nx.shortest_path_length(self.G, root))
        return depth

    def degree_search(self):
        # TODO This needs to be replaced with depth
        sorted_degree = utils.sorted_groupby(self.node_depth().items(), lambda x: x[1], reverse=True)
        for degree, iterable in sorted_degree:
            yield degree, list(zip(*iterable))[0]

    def dependency_graph(self, node):
        """
        Return all parents of the node
        """
        return self.G.subgraph(self.parents(node))

    #async def __aiter__(self):
    #    """
    #    degree_search -> iterate node -> dependency_graph -> generate
    #    """
    #    for degree, nodes in self.degree_search():
    #        for node in nodes:
    #            for n in self.dependency_graph(node).nodes:
    #                arr = await n.generate()
    #                yield n, arr
    #            arr = await node.generate()
    #            yield node, arr

    def __iter__(self):
        for degree, nodes in self.degree_search():
            for node in nodes:
                # TODO reverse order this iter
                for n in self.dependency_graph(node).nodes:
                    # TODO This needs to be fixed
                    yield n
                yield node

    async def generate(self):
        return set(self)
        #return {n: arr async for n, arr in self}

    def centrality(self):
        return nx.eigenvector_centrality(self.G)

    def domain_traversal(self, source=None):
        if source is None:
            source = list(self.G.nodes)[0]
        for node in nx.algorithms.traversal.bfs_edges(self.G, source):
            yield node

    def traversal(self, source=None):
        if source is None:
            source = list(self.G.nodes)[0]
        for node in nx.algorithms.traversal.dfs_edges(self.G, source):
            yield node

    def hydrated_traversal(self):
        pass
