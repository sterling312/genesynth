import pytest
from pytest import fixture
import asyncio
import psutil
from genesynth.worker import *

worker = WorkerRegistry()

class Foo:
    @worker.register
    def foo(self, a):
        return a

class Bar:
    @worker.register
    def foo(self, a):
        return a

    @worker.register
    async def bar(self, a):
        return a

    async def buzz(self, a):
        return a

@worker.register
def foo(a):
    return a

def test_registry():
    r = WorkerRegistry()
    class Bar:
        @r.register
        def bar(self, a):
            return a

    assert len(r) == 1

    b = Bar()
    assert b.bar(1) == 1
    assert Bar.bar.__qualname__ in r
    assert r[Bar.bar.__qualname__](b, 1) == 1

    f = Foo()
    assert f.foo(1) == 1
    assert Foo.foo.__qualname__ in worker
    assert worker[Foo.foo.__qualname__](f, 1) == 1

    assert foo(1) == 1
    assert foo.__qualname__ in worker
    assert worker[foo.__qualname__](1) == 1

@pytest.mark.asyncio
async def test_runner():
    workers = 2
    assert list(worker.keys()) == ['Foo.foo', 'Bar.foo', 'Bar.bar', 'foo']
    assert len(worker) == 4

    runner = Runner(registry=worker, workers=workers)
    assert runner.executor._max_workers == workers

    wraps = runner._wraps(Bar.bar)
    assert wraps.__qualname__ == Bar.bar.__qualname__
    assert wraps.__name__ == 'bar'

    assert not runner.executor._processes
    with pytest.raises(ValueError):
        assert 1 == await runner.run(Bar().foo, 1)
    assert len(runner.executor._processes) <= workers
    assert psutil.pid_exists(list(set(runner.executor._processes))[0])
    assert psutil.Process(list(set(runner.executor._processes))[0]).name() in ('Python', 'python', 'pytest')
    assert 1 == await runner.run(Bar().bar, 1)
    assert len(runner.executor._processes) <= workers
    assert 1 == await runner.run(Bar().buzz, 1)
    assert len(runner.executor._processes) <= workers

