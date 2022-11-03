import pytest
from pytest import fixture
import tempfile
import yaml
import asyncio
import networkx as nx
import numpy as np
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

@fixture
def file():
    with open('foo', 'w+') as fh:
        fh.write('line1\n')
        fh.write('line2\n')
        fh.flush()
        yield fh
    os.remove('foo')

def test_config_to_graph(table):
    G = nx.DiGraph()
    config_to_graph(G, 'table', table)

@fixture
def array_file():
    arr = np.arange(10)    
    with tempfile.NamedTemporaryFile(suffix='.gz') as tmp:
        np.savetxt(tmp.name, arr)
        yield tmp.name

def test_CacheCollection_load_existing_file(array_file): 
    c = CacheCollection('test')

    class Foo:
        name = 'foo'
        _file = array_file
        @c.cache
        async def generate(self):
            return np.array([])

    arr = asyncio.run(Foo().generate())
    np.testing.assert_array_equal(arr, np.arange(10))

def test_write_as_gz(file):
    write_as_gzip(file, 'foo.gz')
    line = gzip.open('foo.gz', 'rb').readline()
    assert line == b'line1\n'

def test_CacheCollection_cache_array():
    c = CacheCollection('test')
    rand = np.random.randint(0, 100, 10)

    class Bar:
        name = 'bar'
        _file = None
        @c.cache
        async def generate(self):
            return rand

        async def write(self, arr):
            np.savetxt(self._file, arr, delimiter='\n')
            
    arr = asyncio.run(Bar().generate())
    np.testing.assert_array_equal(arr, rand)
