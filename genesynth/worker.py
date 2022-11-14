import os
import enum
import asyncio
from multiprocessing import Manager, cpu_count
from concurrent import futures
from genesynth.utils import co_spawn

class WorkloadType(enum.Enum):
    DEFAULT = 'asyncio'
    IO = 'thread'
    CPU = 'process'

WORKER = int(os.environ.get('GENESYNTH_WORKER_COUNT') or cpu_count())

class Registry(dict):
    def add_worker(self, fn):
        self[fn.__qualname__] = fn
        return fn

class Runner:
    def __init__(self, registry, workers=WORKER):
        self.executor = futures.ProcessPoolExecutor(workers)
        self.registry = registry

    @property
    def loop(self):
        return asyncio.get_running_loop()

    def worker(self, fn):
        async def wraps(*args, **kwargs):
            return await asyncio.wrap_future(self.executor.submit(co_spawn, fn, *args, **kwargs), loop=self.loop)
            #return await self.loop.run_in_executor(None, fn(*args, **kwargs))
        self.registry[fn.__qualname__] = wraps
        return fn

    async def run(self, method, *args, **kwargs):
        obj = method.__self__ 
        qualname = f'{obj.__class__.__name__}.{method.__name__}'
        if qualname in self.registry:
            return await self.registry[qualname](obj)
        else:
            return await method(*args, **kwargs)

    def __del__(self, *args, **kwargs):
        self.executor.shutdown()

