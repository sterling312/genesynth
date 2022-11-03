import os
import yaml
import gzip
import tempfile
import networkx as nx
import numpy as np

"""
1. construct graph based on input configuration
2. graph will be created recursively, and requires name to be unique at each level
3. data synthsis will only happen when type is delcared at lowest level within the tree
4. constraint is evaluated at each level with low level first, but overwritten by high level constraint
5. meta.parameter is configuration, constraint is validation
"""

def read_dot(filename):
    return nx.DiGraph(nx.nx_pydot.read_dot(filename))

def load_config(filename):
    with open(filename) as fh:
        data = yaml.safe_load(fh)
    return data

def config_to_graph(G, name, params):
   type = params['type']
   metadata = params.get('metadata')
   constraints = params.get('constraints')
   G.add_node(name, metadata=metadata) # convert constraints into attributes
   properties = params.get('properties')
   if properties is not None:
       for field, attributes in properties.items():
           G.add_edge(name, field) # add relationship type here
           config_to_graph(G, field, attributes)

def write_as_gzip(fh_obj, filename):
    with gzip.open(filename, 'wt') as target:
        if isinstance(fh_obj, str):
            fh_obj = open(fh_obj)
        fh_obj.seek(0)
        for line in fh_obj:
            target.write(line)

class CacheCollection:
    def __init__(self, name):
        self.name = name
        self.dir = tempfile.TemporaryDirectory(prefix=f'{name}_')

    def cache(self, fn):
        async def wrapped(obj, *args, **kwargs):
            if obj._file is None:
                arr = await fn(obj, *args, **kwargs)
                obj._file = os.path.join(self.dir.name, f'{obj.name}.gz')
                await obj.write(arr)
                return arr
            else:
                return np.loadtxt(obj._file)
        return wrapped
