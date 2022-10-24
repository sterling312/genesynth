import pytest
from pytest import fixture
import asyncio
from dataclasses import dataclass
import networkx as nx
import numpy as np
from genesynth.orchestration import *
from genesynth.types import SerialFixture

@fixture
def node():
    yield SerialFixture(name='serial', size=10)

@fixture
def o():
    G = nx.DiGraph()
    return Orchestration(G, worker=1)

def test_process(o, node):
    arr = asyncio.run(o.process(node))
    np.testing.assert_array_equal(arr, np.arange(10))
    
def test_thread(o, node):
    arr = asyncio.run(o.thread(node))
    np.testing.assert_array_equal(arr, np.arange(10))
    
def test_asyncio(o, node):
    arr = asyncio.run(o.asyncio(node))
    np.testing.assert_array_equal(arr, np.arange(10))
