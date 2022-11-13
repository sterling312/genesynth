import enum
import asyncio
from multiprocessing import Manager, cpu_count
from concurrent import futures
from genesynth.utils import co_spawn

class WorkloadType(enum.Enum):
    DEFAULT = 'asyncio'
    IO = 'thread'
    CPU = 'process'

class Runner:
    registry = {}
    def __init__(self, workers=cpu_count()):
        self.executor = futures.ProcessPoolExecutor(workers)

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

