import enum
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass, field
import numpy as np
from scipy import stats
from genesynth import mat

def reseed(seed=None):
    np.random.seed(seed)

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
    name: str
    size: int
    workload = WorkloadType.IO
    null = None
    _file = None

    def mask(self):
        pass

    def dist(self):
        pass

    @staticmethod
    def index_value(arr):
        return mat.index_value(arr)
        
    async def generate(self):
        raise NotImplementedError(f'{self.__class__.__name__} does not have generate defined')

    async def write(self, arr):
        print(arr)

@dataclass(unsafe_hash=True)
class BaseNumberFixture(BaseMask):
    null = np.nan
    pass

@dataclass(unsafe_hash=True)
class BaseTextFixture(BaseMask):
    pass

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
    pass
