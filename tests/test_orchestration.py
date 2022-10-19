import pytest
from pytest import fixture
import asyncio
from dataclasses import dataclass
import networkx as nx
from genesynth.orchestration import *

@dataclass
class TestType:
    sleep: int = 1
    async def generate(self):
        asyncio.sleep(self.sleep)
        return self.sleep

@fixture
def node():
    yield TestType()

@fixture
def o():
    G = nx.DiGraph()
    return Orchestration(G, worker=1)

def test_process(o, node):
    assert asyncio.run(o.process(node)) == 1
    
def test_thread(o, node):
    assert asyncio.run(o.thread(node)) == 1
    
def test_asyncio(o, node):
    assert asyncio.run(o.asyncio(node)) == 1
    
