from itertools import groupby
from functools import wraps
from contextlib import contextmanager
import asyncio
from concurrent import futures

def sorted_groupby(arr, func, reverse=False):
    return groupby(sorted(arr, key=func, reverse=reverse), key=func)

def spawn(fn, *args, **kwargs):
    return asyncio.run(fn(*args, **kwargs))

def co_spawn(coro):
    return asyncio.run(coro)

async def waits(*futures, timeout=None):
    done, notdone = futures.wait(futures, timeout=timeout, return_when='FIRST_COMPLETED')
    return done.pop().result()

async def wait(future, check_interval=0.1):
    while not future.done():
        await asyncio.sleep(check_interval)
    return future.result()

def iterate_lines(*filenames):
    filehandlers = []
    for filename in  filenames:
        filehandlers.append(open(filename, 'rb'))
    for lines in zip(*filehandlers):
        yield [line.rstrip(b'\n') for line in lines]
