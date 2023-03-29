import pytest
from pytest import fixture
import asyncio
from genesynth.io import *
from genesynth.graph import *
from genesynth.model import *

@fixture
def basic_graph():
    G = read_dot('tests/graph.dot')
    yield G

@fixture
def G(basic_graph):
    graph = Graph(basic_graph, name='root')
    yield graph 

@fixture(scope='function')
def fixture_graph():
    reseed(1)
    G = nx.DiGraph()
    size = 10
    col1 = SerialFixture(name='col1', size=size)
    col2 = IntegerFixture(name='col2', size=size, min=0, max=10)
    G.add_node(col1)
    G.add_node(col2)
    yield G

@fixture
def model(fixture_graph):
    graph = Graph(fixture_graph, name='table')
    yield graph 

def test_parents(G):
    parent = G.parents('2')
    assert set(parent.nodes) == {'root'}

def test_children(G):
    children = G.children('3')
    assert set(children.nodes) == {'9', '6', '7'}

def test_node_degree(G):
    degree = G.node_degree()
    assert degree['root'] == 0
    assert degree['2'] == 1
    assert degree['9'] == 2
    assert degree['13'] == 3

def test_degree_search(G):
    depth = {degree: nodes for degree, nodes in  G.degree_search()}
    assert depth[0] == ('root',)
    assert '9' in depth[2]
    assert '6' in depth[3]

def test_domain_traversal(G):
    nodes = list(G.domain_traversal('2'))
    assert nodes == [('2', '3'), ('2', '4'), ('2', '5'), ('3', '6'), ('3', '7'), ('7', '9')]

def test_traversal(G):
    nodes = list(G.traversal('2'))
    assert nodes == [('2', '3'), ('3', '6'), ('3', '7'), ('7', '9'), ('2', '4'), ('2', '5')]

def test_generate(model):
    depth = {degree: nodes for degree, nodes in  model.degree_search()}

@fixture
def graph():
    size = 10
    G = nx.DiGraph()
    field1 = BooleanFixture(name='field1', size=size)
    field2 = IntegerFixture(name='field2', size=size, min=0, max=10)
    fields = {'field1': field1, 'field2': field2}
    json = BaseMapFixture(name='json', size=size, children=fields)
    col1 = SerialFixture(name='col1', size=size)
    col2 = IntegerFixture(name='col2', size=size, min=0, max=10)
    children = {'col1': col1, 'col2': col2, 'json': json}
    table = BaseMapFixture(name='table', size=size, children=children)
    G.add_node(table)
    G.add_node(col1)
    G.add_node(col2)
    G.add_edge(table, col1)
    G.add_edge(table, col2)
    G.add_edge(json, field1)
    G.add_edge(json, field2)
    G.add_edge(table, json)
    return G

def test_nested(graph):
    nodes = list(set(graph))
    assert len(nodes) == 6
