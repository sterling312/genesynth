"""
Worker is the uilitiy library that handles how to create worker process or other processing methodologies.
"""

import os
import enum
import asyncio
import functools
from multiprocessing import Manager, cpu_count
from concurrent import futures
from genesynth.utils import spawn

class WorkloadType(enum.Enum):
    DEFAULT = 'asyncio'
    IO = 'thread'
    CPU = 'process'

class WorkerRegistry(dict):
    def register(self, fn):
        self[fn.__qualname__] = fn
        return fn

class Runner:
    def __init__(self, registry, workers=cpu_count()):
        self.registry = registry
        self.max_workers = workers
        self.executor = futures.ProcessPoolExecutor(workers)
        self.methods = {qualname: self._wraps(fn) for qualname, fn in registry.items()}

    @property
    def loop(self):
        return asyncio.get_running_loop()

    def _wraps(self, fn):
        @functools.wraps(fn)
        async def wraps(*args, **kwargs):
            return await asyncio.wrap_future(self.executor.submit(spawn, fn, *args, **kwargs), loop=self.loop)
        return wraps

    async def run(self, method, *args, **kwargs):
        obj = method.__self__ 
        qualname = f'{obj.__class__.__name__}.{method.__name__}'
        if qualname in self.methods:
            return await self.methods[qualname](obj, *args, **kwargs)
        else:
            return await method(*args, **kwargs)
