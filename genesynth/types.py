import os
import enum
import random
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field
import numpy as np
from scipy import stats
from mimesis import Generic
from mimesis.random import Random
from mimesis.locales import Locale
from mimesis.builtins import USASpecProvider
from genesynth.io import CacheCollection
from genesynth import mat

def reseed(seed=None):
    BaseMask.seed = seed
    np.random.seed(seed)
    random.seed(seed)

class datatypes(dict):
    def register(self, fn):
        self[fn.__name__] = fn
        return fn

class Hashabledict(dict):
    def __hash__(self):
        return hash(frozenset(self))

class WorkloadType(enum.Enum):
    DEFAULT = 'asyncio'
    IO = 'thread'
    CPU = 'process'

@dataclass(unsafe_hash=True)
class BaseMask:
    seed = None
    name: str
    size: int
    workload = WorkloadType.IO
    null = None
    _index = None
    _mask = None
    _file = None
    _path = None

    def mask(self):
        pass

    def dist(self):
        pass

    @staticmethod
    def index_value(arr):
        return arr[mat.incremental_index(arr)]
        
    async def generate(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not have generate defined')

    async def write(self):
        if self._file is not None:
            return
        arr = await self.generate()
        if self._path is not None:
            filename = os.path.join(self._path, self.name)
        else:
            filename = self.name
        np.savetxt(filename, arr, fmt="%s", delimiter='\n')
        self._file = filename

@dataclass(unsafe_hash=True)
class BaseNumberFixture(BaseMask):
    null = np.nan
    pass

@dataclass(unsafe_hash=True)
class BaseTextFixture(BaseMask):
    length: int = None

    def __post_init__(self):
        self.random = Random(self.seed)

    async def generate(self):
        return np.array([self.random.randstr()[:self.length] for _ in range(self.size)])

@dataclass(unsafe_hash=True)
class BaseTimestamp(BaseMask):
    pass

@dataclass(unsafe_hash=True)
class BaseForeign(BaseMask):
    depends_on: Any
    async def generate(self):
        arr = await self.depends_on.generate()
        return arr

@dataclass(unsafe_hash=True)
class BaseArrayFixture(BaseMask):
    null = []
    children: tuple = field(default_factory=tuple)

    def __post_init__(self):
        self.children = tuple(self.children)

    async def __aiter__(self):
        for node in self.children:
            node.size = self.size
            yield await node.generate()

    async def generate(self):
        return [arr async for arr in self]

@dataclass(unsafe_hash=True)
class BaseMapFixture(BaseMask):
    null = {}
    children: dict = field(default_factory=dict)

    def __post_init__(self):
        self.children = Hashabledict(self.children)

    async def __aiter__(self):
        for key, node in self.children.items():
            node.size = self.size
            arr = await node.generate()
            yield key, arr

    async def generate(self):
        return {key: arr async for key, arr in self}

@dataclass(unsafe_hash=True)
class IntegerFixture(BaseNumberFixture):
    min: int
    max: int
    null = None

    async def generate(self):
        return np.random.randint(self.min, self.max, self.size)

@dataclass(unsafe_hash=True)
class SerialFixture(BaseNumberFixture):
    min: int = 0
    step: int = 1
    null = 0

    async def generate(self):
        return np.arange(self.min, self.min + self.size * self.step, self.step)

@dataclass(unsafe_hash=True)
class BooleanFixture(BaseNumberFixture):
    async def generate(self):
        return np.random.randint(0, 2, self.size).astype(bool)

@dataclass(unsafe_hash=True)
class FloatFixture(BaseNumberFixture):
    min: int
    max: int

    async def generate(self):
        return stats.uniform.rvs(self.min, self.max, self.size)

@dataclass(unsafe_hash=True)
class DecimalFixture(FloatFixture):
    precision: int
    scale: int

    async def generate(self):
        arr = await super().generate()
        return np.round(arr, self.scale)

@dataclass(unsafe_hash=True)
class StringFixture(BaseTextFixture):
    null = ''
    subtype: str = 'text'
    field: str = 'sentence'
    locale = Locale.EN

    def __post_init__(self):
        self.generic = Generic(locale=self.locale, seed=self.seed)

    async def generate(self):
        func = getattr(self.generic, self.subtype)
        if self.field is not None:
            func = getattr(func, self.field)
        return np.array([func()[:self.length] for _ in range(self.size)])
