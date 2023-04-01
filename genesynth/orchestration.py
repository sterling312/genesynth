"""
Orchestration is sorely responsible for integration graph and schedule processing based on the correct order.
This module should ONLY dictate the dependency tree based on processing optimization and not entity relationship.
Orchestration can use higher level datatypes from Model to do garbage collection to optimize for cache datasize.
"""

import sys
import logging
import typing
import enum
import asyncio
import uvloop
import networkx as nx
from dataclasses import dataclass
from collections import ChainMap
from multiprocessing import Manager, cpu_count
from concurrent import futures
from genesynth.types import Hashabledict, BaseForeign
from genesynth.graph import Graph, find_node, find_child_node
from genesynth.model import worker, types, BaseDataModel, WorkloadType
from genesynth.extensions import extensions
from genesynth.worker import Runner
from genesynth.io import load_config
from genesynth.utils import spawn, wait
from genesynth.constraints import *

if sys.version_info < (3, 11):
    uvloop.install()

logger = logging.getLogger(__name__)

datatypes = ChainMap(types, extensions)

class Constraint(enum.Enum):
    unique = 1 
    notnull = 2
    incremental = 3
    uuid = 4

class Node(enum.Enum):
    unique = 1 # node contains no duplicated value
    notnull = 2 # node contains no empty value
    incremental = 3 # node increases over index
    subset = 4 # node contains value within the set (between is just (a...b) eps R)

class Relationship(enum.Enum):
    child = 1 # node is a child of parent
    subset = 2 # node contains subset of copy of parent
    index = 3 # node contains same index as parent
    identity = 4 # node contains exact copy of parent
    incremental_index = 5 # node contains increasing index as parent

def config_to_graph(G, fullname, params, size=0):
    name = fullname.rsplit('.', 1)[-1]
    type = params['type']
    metadata = params.get('metadata', {})
    metadata['size'] = metadata.get('size') or size
    metadata['sep'] = metadata.get('sep', '')
    foreign = metadata.pop('foreign', None)
    constraints = params.get('constraints')
    if foreign:
        depends_on = f'root.{foreign["name"]}'
        node = BaseForeign.from_params(name=fullname, graph=G, depends_on=depends_on, metadata=metadata, **metadata)
    else:
        node = datatypes[type].from_params(name=fullname, metadata=metadata, **metadata)
    properties = params.get('properties')
    if properties is not None:
        children = {}
        for field, attributes in properties.items():
            field_fullname = f'{fullname}.{field}'
            child = config_to_graph(G, field_fullname, attributes, size=size)
            children[child] = child
        node.children = Hashabledict(children)
        # add node to graph after setting data field children
        for child in children.values():
            G.add_edge(node, child) # add relationship type here
    G.add_node(node, label=fullname, xlabel=name, _id=fullname, type=type, metadata=metadata) # convert constraints into attributes
    return node

class Orchestration:
    """
    Handles processing optimization by determing the type of worker that can be used for each data type.
    """
    def __init__(self, graph, thread=10, runner=Runner(registry=worker)):
        self.graph = graph
        self.runner = runner
        self.max_workers = runner.max_workers * thread
        self.queue = asyncio.Queue(self.max_workers)
        self.executor = futures.ThreadPoolExecutor(thread)

    @classmethod
    def read_yaml(cls, filename, name='root'):
        data = load_config(filename)
        size = data['metadata']['size']
        G = nx.DiGraph()
        config_to_graph(G, name, data, size=size)
        graph = Graph(G, name=name, metadata=data['metadata'])
        for n in graph.nodes:
            if isinstance(n, BaseForeign):
                n.resolve_fkey_edge()
        return cls(graph)

    async def walk(self):
        # TODO check to make sure this is correct
        for parent, node in self.graph.traversal():
            logger.debug(node)
            await self.queue.put(node)

    @property
    def root(self):
        return next(iter(self.graph.root))

    async def __aiter__(self):
        """
        graph.iter: degree_search -> iterate node -> dependency_graph -> generate
        orchestraion.iter: type check -> aggregate by nearest map/array -> garbage collect
        """
        #for node in self.graph.G:
        #    arr = await self.generate(node)
        #    await node.write(arr)

        # TODO Add reduce step from DataModel and garbage collect
        await self.walk()
        while self.queue.qsize() > 0:
            node = await self.queue.get()
            arr = await self.generate(node)
            logger.debug(arr)
            try:
                await node.write()
            except TypeError:
                await node.write(arr)

    def run(self):
        loop = asyncio.get_running_loop()
        if loop and loop.is_running():
            loop.create_task(self.__aiter__())
        else:
            asyncio.run(self.__aiter__())

    async def generate(self, node):
        # TODO replace this with graph traversal and task queue/dequeue
        if isinstance(node, BaseDataModel):
            return await self.asyncio(node)
        elif node.workload == WorkloadType.IO:
            return await self.thread(node)
        elif node.workload == WorkloadType.CPU:
            return await self.process(node)
        else:
            return await self.asyncio(node)

    async def process(self, node):
        return await self.runner.run(node.generate)

    async def thread(self, node):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self.executor, spawn, node.generate)

    async def asyncio(self, node):
        return await node.generate()
