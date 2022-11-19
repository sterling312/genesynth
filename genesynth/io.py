import os
import logging
import yaml
import gzip
import json
import yaml
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

logger = logging.getLogger(__name__)

def read_dot(filename):
    return nx.DiGraph(nx.nx_pydot.read_dot(filename))

def load_config(filename):
    with open(filename) as fh:
        data = yaml.safe_load(fh)
    return data

def config_to_graph(fullname, params, G=nx.Graph()):
    name = fullname.rsplit('.', 1)[-1]
    type = params['type']
    metadata = params.get('metadata')
    constraints = params.get('constraints')
    G.add_node(name, label=name, _id=fullname, type=type, metadata=metadata) # convert constraints into attributes
    properties = params.get('properties')
    if properties is not None:
        for field, attributes in properties.items():
            G.add_edge(name, field) # add relationship type here
            field_fullname = f'{fullname}.{field}'
            config_to_graph(field_fullname, attributes, G=G)
    return G

def write_as_gzip(fh_obj, filename):
    with gzip.open(filename, 'wt') as fh:
        if isinstance(fh_obj, str):
            fh_obj = open(fh_obj)
        fh_obj.seek(0)
        for line in fh_obj:
            fh.write(line)

def write_as_json(fh_obj, filename, header=False):
    with open(filename, 'w') as fh:
        if isinstance(fh_obj, str):
            fh_obj = open(fh_obj)
        fh_obj.seek(0)
        if header:
            line = fh_obj.readline()
        records = [json.loads(line.rstrip('\n')) for line in fh_obj]
        json.dump(records, fh)

def write_as_yaml(fh_obj, filename, header=False):
    with open(filename, 'w') as fh:
        if isinstance(fh_obj, str):
            fh_obj = open(fh_obj)
        fh_obj.seek(0)
        if header:
            line = fh_obj.readline()
        records = [json.loads(line.rstrip('\n')) for line in fh_obj]
        yaml.dump(records, fh)

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
