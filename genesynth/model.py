import os
import shutil
import glob
import enum
import json
import asyncio
import tempfile
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import numpy as np
from scipy import stats
from genesynth.io import load_config, config_to_graph
from genesynth.types import *
from genesynth.utils import iterate_lines

@dataclass
class BaseDataModel(BaseMapFixture):
    """
    Handles data structure grouping based on the graph.
    Mainly deals with local root level structure hubs based on data type.
    Also handles aggregating cached resources and garbage collection.
    name: str - i.e. name of the table
    schema: str - i.e. namespace of the database such as schema
    metadata: dict[str, str] - data model specific config (required) of the dataset
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
        super().__post_init__()
        self._dir = tempfile.TemporaryDirectory()

    async def __aiter__(self):
        pass

    async def generate(self):
        gens = [n.generate() for n in self.children.values()]
        done, pending = await asyncio.wait(gens)
        return [await f for f in done]

    @property
    def sep(self):
        return self.metadata.get('sep', '').encode('utf-8')

    @asynccontextmanager
    async def _filename(self, path=None):
        if path is None:
            filename = os.path.join(self._dir.name, self.name)
        else:
            filename = os.path.join(path, self.name)
        with open(filename, 'wb+') as fh:
            yield fh

    async def merge(self, nodes, path=None):
        filenames = [node._file for node in nodes]
        async with self._filename(path) as fh:
            for lines in iterate_lines(*filenames):
                fh.write(self.sep.join(lines))
                fh.write(b'\n')
                await asyncio.sleep(0)
            fh.seek(0)
            length = len(list(fh))
            if self.has_header:
                length -= 1
        assert length == self.size, f'expected {self.size} data row, got {length}'

    async def write(self):
        gens = []
        for n in self.children.values():
            gens.append(n)
            n._path = self._dir.name
            # TODO defer this to orchestrator
            await n.write()
        await self.merge(gens, path=self._dir.name)
        self._file = os.path.join(self._dir.name, self.name)

    async def save(self, filename):
        if self._file is None:
            await self.write()
        shutil.copy(self._file, filename)


@dataclass
class TableDataModel(BaseDataModel):
    # TODO change this to have default keys
    metadata: dict = field(default_factory=dict)

    @property
    def has_header(self):
        return self.metadata.get('header')

    @property
    def has_footer(self):
        return self.metadata.get('footer')

    @property
    def header(self):
        if isinstance(self.metadata['header'], bool):
            return self.sep.join(n.name.encode('utf-8') for n in self.children.values())
        return self.metadata['header'].encode('utf-8')

    @property
    def footer(self):
        return self.metadata.get('footer', '').encode('utf-8')

    @asynccontextmanager
    async def _filename(self, path=None):
        if path is None:
            filename = os.path.join(self._dir.name, self.name)
        else:
            filename = os.path.join(path, self.name)
        with open(filename, 'wb+') as fh:
            if self.has_header:
                fh.write(self.header)
                fh.write(b'\n')
            yield fh
            if self.has_footer:
                fh.write(self.footer)


@dataclass
class JsonDataModel(BaseDataModel):
    async def merge(self, nodes, path=None):
        filenames = {node.name: node._file for node in nodes}
        async with self._filename(path) as fh:
            for lines in iterate_lines(*filenames.values()):
                # TODO add support for array
                record = {key: json.loads(value) if isinstance(node, BaseMapFixture) else value 
                            for node, key, value in zip(nodes, filenames.keys(), lines)}
                fh.write(json.dumps(record, default=lambda x: x.decode('ascii')).encode('utf-8'))
                fh.write(b'\n')
                await asyncio.sleep(0)
            fh.seek(0)
            length = len(list(fh))
        assert length == self.size, f'expected {self.size} data row, got {length}'

    async def write(self):
        gens = []
        if self._path is None:
            path = self._dir.name
        else:
            path = os.path.join(self._path, self.name)
        if not os.path.isdir(path):
            os.mkdir(path)
        for n in self.children.values():
            gens.append(n)
            # TODO defer this to orchestrator
            await n.write()
        await self.merge(gens, path)
        self._file = os.path.join(path, self.name)
