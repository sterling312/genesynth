"""
Core library that determines how data will be generated based on respective types (dataclass).
It will be possible to represent each type as a protocol buffer for serialization.
All type must provide async generate method and optional write method.
"""

import os
import enum
import random
import hashlib
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, date, time
from functools import cache, cached_property
import numpy as np
import pandas as pd
from scipy import stats
from mimesis import Generic
from mimesis.random import Random
from mimesis.locales import Locale
from mimesis.builtins import USASpecProvider
from genesynth.worker import WorkloadType, Runner, WorkerRegistry
from genesynth.constraints import *
from genesynth.graph import nx, find_node, find_child_node
from genesynth.utils import sorted_groupby
from genesynth import mat

def reseed(seed=None):
    BaseMask.seed = seed
    np.random.seed(seed)
    random.seed(seed)

worker = WorkerRegistry()

class Datatypes(dict):
    def register(self, alias: List):
        def wraps(obj):
            assert BaseMask in obj.__mro__, f'type {obj.__name__} needs to be subclass of BaseMask'
            for name in alias:
                self[name] = obj
            return obj
        return wraps

class Hashabledict(dict):
    def __hash__(self):
        return hash(frozenset(self))

types = Datatypes()
datatypes = types

@dataclass(unsafe_hash=True)
class BaseMask:
    is_data = True
    seed = None
    name: str
    size: int
    workload = WorkloadType.IO
    null = None
    _metadata = {}
    _constraints = []
    _index = None
    _mask = None
    _file = None # cache filename
    _hashfile = True
    _path = None # cache directory
    _defer = None # parent node if deferred

    # TODO handle notnull and unique constraits

    @classmethod
    def from_params(cls, metadata={}, constraints=[], **kwargs):
        # TODO add type conversion based on constraints
        fields = set(cls.__dataclass_fields__.keys())
        keys = set(kwargs.keys())
        params = {field: kwargs[field] for field in fields & keys}
        obj = cls(**params)
        obj._metadata = metadata
        obj._constraints = cls.unpack_constraints(constraints)
        return obj

    @staticmethod
    def unpack_constraints(constraints):
        return {k: list(filter(None, (i[-1] for i in v))) 
            for k, v in sorted_groupby(constraints, lambda x: x[0])}

    @cache
    def mask(self):
        if 'notnull' in self._constraints:
            return mat.null_percent(self.size, percent=0)
        elif 'nullable' in self._constraints:
            mask = mat.identity(self.size, matmul=True)
            for value in self._constraints['nullable']:
                mask &= mat.null_percent(self.size, percent=value)
            return mask

    @cache
    def dist(self, model='uniform', **kwargs):
        params = {'loc': 0, 'scale': 1}
        params.update(kwargs)
        return mat.stats_model_generate(self.size, model=model, **params)

    @staticmethod
    def index_value(arr):
        return mat.ordered_index(arr)

    @staticmethod
    def subset_index(arr, subset):
        index = mat.identity(arr.size)
        mask = mat.identity(self.size, matmul=True) == False
        for unique in np.unique(subset):
            mask |= mat.mask_index(arr, unique)
        return index[mask]

    def index(self, arr):
        index = mat.identity(self.size)
        if 'sorted' in self._constraints:
            index = mat.ordered_index(arr)
        return index

    def apply_index(self, arr, null=''):
        mask = self.mask()
        index = self.index(arr)
        return mat.nullable(arr[index].astype(str), mask=mask, null=null).filled()

    async def generate(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not have generate defined')

    async def write(self):
        if self._file is not None:
            return
        if isinstance(self, BaseArrayFixture):
            arr = await self.generate()
            arr = np.array(arr)
            if arr.ndim > 2:
                arr = np.squeeze(arr) # TODO temporary hack. need to figure out how to output this better
        else:
            arr = await self.generate()
        if self._path is not None:
            if self._hashfile:
                filename = os.path.join(self._path, hashlib.md5(self.name.encode('ascii')).hexdigest())
            else:
                filename = os.path.join(self._path, self.name)
        else:
            if self._hashfile:
                filename = hashlib.md5(self.name.encode('ascii')).hexdigest()
            else:
                filename = self.name
        np.savetxt(filename, arr, fmt='%s', delimiter='\n')
        self._file = filename

    def __str__(self):
        return f"{self.__class__.__name__}(name='{self.name}', size={self.size})"

    def __del__(self, *args, **kwargs):
        if self._file and os.path.isfile(self._file):
            os.remove(self._file)

@dataclass(unsafe_hash=True)
class BaseNumberFixture(BaseMask):
    null = np.nan
    pass

@types.register(['enum'])
@dataclass(unsafe_hash=True)
class BaseTextFixture(BaseMask):
    options: tuple = field(default_factory=tuple)
    replace: bool = True

    def __post_init__(self):
        self.options = tuple(self.options)

    async def generate(self):
        arr = mat.sample(self.size, self.options, replace=replace)
        return self.apply_index(arr)

@types.register(['text'])
@dataclass(unsafe_hash=True)
class BaseTextFixture(BaseMask):
    length: int = None

    def __post_init__(self):
        self.random = Random(self.seed)

    async def generate(self):
        arr = np.array([self.random.randstr()[:self.length] for _ in range(self.size)])
        return self.apply_index(arr)

@types.register(['timestamp', 'datetime'])
@dataclass(unsafe_hash=True)
class BaseTimestamp(BaseMask):
    min: datetime = datetime.fromtimestamp(0)
    max: datetime = datetime.now()

    async def generate(self):
        arr = pd.date_range(self.min, self.max, periods=self.size).to_pydatetime()
        return self.apply_index(arr)

@types.register(['date'])
@dataclass(unsafe_hash=True)
class BaseDate(BaseTimestamp):
    async def generate(self):
        arr = pd.date_range(self.min, self.max, periods=self.size).date
        return self.apply_index(arr)

@types.register(['time'])
@dataclass(unsafe_hash=True)
class BaseTime(BaseTimestamp):
    min: time = time(0)
    max: time = time(23, 59, 59)

    async def generate(self):
        min = datetime.fromtimestamp(0).replace(hour=self.min.hour, minute=self.min.minute,
            second=self.min.second, microsecond=self.min.microsecond)
        max = datetime.fromtimestamp(0).replace(hour=self.max.hour, minute=self.max.minute,
            second=self.max.second, microsecond=self.max.microsecond)
        arr = pd.date_range(min, max, periods=self.size).time
        return self.apply_index(arr)

@types.register(['foreign'])
@dataclass(unsafe_hash=True)
class BaseForeign(BaseMask):
    depends_on: str
    graph: nx.DiGraph
    _node = None

    @property
    def node(self):
        if self._node is None:
            parent, *child = self.depends_on.split('.')
            self._node = find_child_node(self.graph, parent, *child)
            self._node._path = self._path
            self.resolve_fkey_edge()
        return self._node

    def resolve_fkey_edge(self):
        if (self.node, self) not in self.graph.edges:
            self.graph.add_edge(self.node, self, label='fkey', type='fkey')

    async def generate(self):
        arr = await self.node.generate()
        return self.apply_index(arr)

@types.register(['array', 'list', 'tuple'])
@dataclass(unsafe_hash=True)
class BaseArrayFixture(BaseMask):
    null = []
    children: tuple = field(default_factory=tuple)

    def __post_init__(self):
        self.children = tuple(self.children)

    async def __aiter__(self):
        for node in self.children:
            if isinstance(node, BaseMask):
                node.size = self.size
                yield await node.generate()
            else:
                yield node

    async def generate(self):
        return [arr async for arr in self]

@types.register(['map', 'struct'])
@dataclass(unsafe_hash=True)
class BaseMapFixture(BaseMask):
    null = {}
    children: dict = field(default_factory=dict)

    def __post_init__(self):
        self.children = Hashabledict(self.children)

    async def __aiter__(self):
        for key, node in self.children.items():
            if isinstance(node, BaseMask):
                node.size = self.size
                arr = await node.generate()
                yield key, arr
            else:
                yield node

    async def generate(self):
        return {key: arr async for key, arr in self}

@types.register(['integer'])
@dataclass(unsafe_hash=True)
class IntegerFixture(BaseNumberFixture):
    min: int = 0
    max: int = 100
    null = None

    # TODO add type conversio to Serial when constraint is incremental

    async def generate(self):
        arr = np.random.randint(self.min, self.max, self.size)
        return self.apply_index(arr)

@types.register(['serial'])
@dataclass(unsafe_hash=True)
class SerialFixture(BaseNumberFixture):
    min: int = 0
    step: int = 1
    null = 0

    async def generate(self):
        arr = np.arange(self.min, self.min + self.size * self.step, self.step)
        return self.apply_index(arr)

@types.register(['boolean'])
@dataclass(unsafe_hash=True)
class BooleanFixture(BaseNumberFixture):
    async def generate(self):
        arr = np.random.randint(0, 2, self.size).astype(bool)
        arr = np.where(arr==True, 'true', np.where(arr==False, 'false', arr))
        return self.apply_index(arr)

@types.register(['float', 'double'])
@dataclass(unsafe_hash=True)
class FloatFixture(BaseNumberFixture):
    min: int = -1
    max: int = 1

    async def generate(self):
        arr = stats.uniform.rvs(self.min, self.max, self.size)
        return self.apply_index(arr)

@types.register(['decimal', 'numeric'])
@dataclass(unsafe_hash=True)
class DecimalFixture(FloatFixture):
    precision: int = 16
    scale: int = 3

    async def generate(self):
        arr = await super().generate()
        arr = np.round(arr, self.scale)
        return self.apply_index(arr)

@types.register(['string'])
@dataclass(unsafe_hash=True)
class StringFixture(BaseTextFixture):
    null = ''
    subtype: str = 'text'
    field: str = 'sentence'
    locale = Locale.EN

    # TODO set field to uuid when constraint is uuid

    def __post_init__(self):
        self.generic = Generic(locale=self.locale, seed=self.seed)

    @worker.register
    async def generate(self):
        func = getattr(self.generic, self.subtype)
        if self.field is not None:
            func = getattr(func, self.field)
        arr = np.array([str(func())[:self.length] for _ in range(self.size)])
        return self.apply_index(arr)

    @worker.register
    async def write(self):
        return await super().write()

@types.register(['password'])
@dataclass(unsafe_hash=True)
class BcryptPassword(BaseTextFixture):
    rounds: int = 12
    prefix: str = '2b'

    async def generate(self):
        arr = np.array([f'${self.prefix}${self.rounds}${self.random.randstr(length=53)}' for _ in range(self.size)])
        return self.apply_index(arr)
