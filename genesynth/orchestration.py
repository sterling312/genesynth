import typing
import enum
import asyncio
import uvloop
from dataclasses import dataclass
from concurrent import futures
from genesynth.graph import Graph
from genesynth.model import WorkloadType, DataModel
from genesynth.io import load_config, config_to_graph, CacheFile
from genesynth.utils import spawn, co_spawn, wait

uvloop.install()

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
    incremental_index = 3 # node contains increasing index as parent

class Orchestration:
    """
    Handles processing optimization by determing the type of worker that can be used for each data type.
    """
    def __init__(self, graph, worker=4):
        self.graph = graph
        self.pool = futures.ProcessPoolExecutor(worker)

    #@classmethod
    #def read_yaml(cls, filename):
    #    data = load_config(filename)

    async def __aiter__(self):
        """
        graph.iter: degree_search -> iterate node -> dependency_graph -> generate
        orchestraion.iter: type check -> aggregate by nearest map/array -> garbage collect
        """
        for node in self.graph:
            arr = await self.generate(node)
            await node.write(arr)
        # TODO  Add reduce step from DataModel and garbage collect

    async def generate(self, node):
        if node.workload == WorkloadType.IO:
            return await self.thread(node)
        elif node.workload == WorkloadType.CPU:
            return await self.process(node)
        else:
            return await self.asyncio(node)

    async def process(self, node):
        future = self.pool.submit(spawn, node.generate)
        return await wait(future)

    async def thread(self, node):
        loop = asyncio.get_running_loop()
        with futures.ThreadPoolExecutor(1) as executor:
            return await loop.run_in_executor(executor, co_spawn, node.generate())

    async def asyncio(self, node):
        return await node.generate()
