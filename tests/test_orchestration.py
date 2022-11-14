import pytest
from pytest import fixture
import asyncio
from dataclasses import dataclass
import networkx as nx
import numpy as np
from genesynth.orchestration import *
from genesynth.worker import Runner
from genesynth.types import reseed, registry, SerialFixture, StringFixture

@fixture
def node():
    reseed(1)
    yield SerialFixture(name='serial', size=10)

@fixture
def string():
    reseed(1)
    yield StringFixture(name='text', field='word', size=10)

@fixture
def o():
    G = nx.DiGraph()
    runner = Runner(registry=registry)
    return Orchestration(G, runner=runner)

def test_process(o, node):
    arr = asyncio.run(o.process(node))
    np.testing.assert_array_equal(arr, np.arange(10))

def test_worker_process(o, string):
    arr = asyncio.run(o.process(string))
    np.testing.assert_array_equal(arr, ['carol', 'square', 'returned', 'diary', 'lab', 'indicators', 'patterns', 'scenes', 'bi', 'alerts'])

def test_thread(o, node):
    arr = asyncio.run(o.thread(node))
    np.testing.assert_array_equal(arr, np.arange(10))

def test_asyncio(o, node):
    arr = asyncio.run(o.asyncio(node))
    np.testing.assert_array_equal(arr, np.arange(10))
