"""
IO is the utility library that manages how config and data gets loaded into the library as well as how it is written out.
"""

import os
import logging
import yaml
import gzip
import json
import yaml
import tempfile
import networkx as nx
import numpy as np
from genesynth.types import Hashabledict
from genesynth.extensions import datatypes
from genesynth.constraints import *

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

def schema_to_graph(G, fullname, params, size=0, root='root'):
    # TODO move this logic into io.py without disrupting package dependency
    # TODO incorporate Node and Relationship into node
    # TODO incorporate Constraint into node
    name = fullname.rsplit('.', 1)[-1]
    container = None
    type = params['type']
    if isinstance(type, (list, tuple)):
        type = type[0]
        container = 'array'
    elif type.startswith('[') and type.endswith(']'):
        type = type.strip('[]')
        container = 'array'
    metadata = params.get('metadata', {})
    metadata['size'] = metadata.get('size') or size
    metadata['sep'] = metadata.get('sep', '')
    foreign = metadata.pop('foreign', None)
    constraints = params.get('constraints')
    if foreign:
        depends_on = f'{root}.{foreign["name"]}'
        node = datatypes['foreign'].from_params(name=fullname, graph=G, depends_on=depends_on, metadata=metadata, **metadata)
    elif container == 'array' and type == 'json':
        node = datatypes['json_array'].from_params(name=fullname, metadata=metadata, **metadata)
    elif container == 'array':
        node = datatypes['array'].from_params(name=fullname, metadata=metadata, **metadata)
    else:
        node = datatypes[type].from_params(name=fullname, metadata=metadata, **metadata)
    properties = params.get('properties')
    if properties is not None:
        children = {}
        for field, attributes in properties.items():
            field_fullname = f'{fullname}.{field}'
            child = schema_to_graph(G, field_fullname, attributes, size=size, root=root)
            children[child] = child
        if container == 'array' and type != 'json':
            node.children = tuple(children)
        else:
            node.children = Hashabledict(children)
        # add node to graph after setting data field children
        for child in children.values():
            G.add_edge(node, child) # add relationship type here
    G.add_node(node, label=fullname, xlabel=name, _id=fullname, type=type, metadata=metadata) # convert constraints into attributes
    return node

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
