import os
import enum
import asyncio
import functools
from multiprocessing import Manager, cpu_count
from concurrent import futures
from genesynth.utils import co_spawn

class WorkloadType(enum.Enum):
    DEFAULT = 'asyncio'
    IO = 'thread'
    CPU = 'process'

class Registry(dict):
    def add_worker(self, fn):
        self[fn.__qualname__] = fn
        return fn

class Runner:
    def __init__(self, registry, workers=cpu_count()):
        self.executor = futures.ProcessPoolExecutor(workers)
        self.registry = {qualname: self._wraps(fn) for qualname, fn in registry.items()}

    @property
    def loop(self):
        return asyncio.get_running_loop()

    def _wraps(self, fn):
        @functools.wraps(fn)
        async def wraps(*args, **kwargs):
            return await asyncio.wrap_future(self.executor.submit(co_spawn, fn, *args, **kwargs), loop=self.loop)
        return wraps

    async def run(self, method, *args, **kwargs):
        obj = method.__self__ 
        qualname = f'{obj.__class__.__name__}.{method.__name__}'
        if qualname in self.registry:
            return await self.registry[qualname](obj)
        else:
            return await method(*args, **kwargs)
