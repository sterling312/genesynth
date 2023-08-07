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
from multiprocessing import Manager, cpu_count
from concurrent import futures
from genesynth.types import Hashabledict, BaseForeign
from genesynth.graph import Graph, find_node, find_child_node
from genesynth.model import worker, types, BaseDataModel, WorkloadType
from genesynth.extensions import datatypes
from genesynth.worker import Runner
from genesynth.io import load_config, schema_to_graph
from genesynth.utils import spawn, wait
from genesynth.constraints import *

if sys.version_info < (3, 11):
    uvloop.install()

logger = logging.getLogger(__name__)

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
        schema_to_graph(G, name, data, size=size, root=name)
        graph = Graph(G, name=name, metadata=data['metadata'])
        #for n in graph.nodes:
        #    if isinstance(n, BaseForeign):
        #        n.resolve_fkey_edge()
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
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
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
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, spawn, node.generate)

    async def asyncio(self, node):
        return await node.generate()
