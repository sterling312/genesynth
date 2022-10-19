import os
import yaml
import tempfile
import networkx as nx

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

class CacheFile:
    def __init__(self, dir, name, children=0):
        self.dir = dir
        self.name = name
        self.fh = tempfile.NamedTemporaryFile(dir=self.dir, prefix=f'{name}_')
        self.path = os.path.join(dir, name)

    @property
    def delete(self):
        return self.fh.delete

    @delete.setter
    def delete(self, value):
        self.fh.delete = value

    def clean(self):
        if self.delete:
            self.fh = None
    
