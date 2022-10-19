import pytest
from pytest import fixture
import yaml
import asyncio
import networkx as nx
from genesynth.io import *
from genesynth.orchestration import *

@fixture
def config(): 
    yield load_config('tests/test.yaml')

@fixture
def table(config):
    for table, params in config['properties'].items():
        break
    return params

def test_config_to_graph(table):
    G = nx.DiGraph()
    config_to_graph(G, 'table', table)

    
