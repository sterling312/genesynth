import pytest
from pytest import fixture
import asyncio
from dataclasses import dataclass
import networkx as nx
import numpy as np
from genesynth.orchestration import *
from genesynth.worker import Runner
from genesynth.types import reseed, worker, SerialFixture, StringFixture

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
    runner = Runner(registry=worker)
    return Orchestration(G, runner=runner)

@pytest.mark.asyncio
async def test_process(o, node):
    arr = await o.process(node)
    np.testing.assert_array_equal(arr, np.arange(10))

@pytest.mark.asyncio
async def test_worker_process(o, string):
    arr = await o.process(string)
    np.testing.assert_array_equal(arr, ['carol', 'square', 'returned', 'diary', 'lab', 'indicators', 'patterns', 'scenes', 'bi', 'alerts'])

@pytest.mark.asyncio
async def test_thread(o, node):
    arr = await o.thread(node)
    np.testing.assert_array_equal(arr, np.arange(10))

@pytest.mark.asyncio
async def test_asyncio(o, node):
    arr = await o.asyncio(node)
    np.testing.assert_array_equal(arr, np.arange(10))

def test_orchestration_read_yaml():
    o = Orchestration.read_yaml('tests/test.yaml')
    assert len(o.graph.nodes) == 7
