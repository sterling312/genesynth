import enum
import asyncio
import tempfile
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field
import numpy as np
from scipy import stats
from genesynth.io import load_config, config_to_graph
from genesynth.types import *

@dataclass
class DataModel(BaseMapFixture):
    """
    Handles data structure grouping based on the graph.
    Mainly deals with local root level structure hubs based on data type.
    Also handles aggregating cached resources and garbage collection.
    name: str - i.e. name of the table
    schema: str - i.e. namespace of the database such as schema
    metadata: dict[str, str] - config (required) of the dataset such as row size
    constraints: list[str] - constrait to be added to the data, such as uniqueness check
    label: dict[str, str] - label to be added to the dataset that are not used for generation
    children: list - list od child dependencies
    """
    name: str
    schema: str = None # namespace from metadata
    metadata: dict = field(default_factory=dict)
    constraints: list = field(default_factory=list)
    label: dict = field(default_factory=dict)
    children: dict = field(default_factory=dict)
    workload = WorkloadType.DEFAULT

    def __post_init__(self):
        super().__post_init__(self)
        self._file = tempfile.TemporaryDirectory()

    async def __aiter__(self):
        pass

    async def generate(self):
        gens = [n.generate() for n in self.children.values()]
        done, pending = await asyncio.wait(gens)
        return [await f for f in done]

    async def write(self):
        pass
