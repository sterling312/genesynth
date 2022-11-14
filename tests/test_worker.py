import pytest
from pytest import fixture
import asyncio
from genesynth.worker import *

registry = Registry()

class Foo:
    @registry.to_worker
    def foo(self, a):
        return a

@registry.to_worker
def foo(a):
    return a

def test_registry():
    r = Registry()
    class Bar:
        @r.to_worker
        def bar(self, a):
            return a

    b = Bar()
    assert b.bar(1) == 1
    assert Bar.bar.__qualname__ in r
    assert r[Bar.bar.__qualname__](b, 1) == 1

    f = Foo()
    assert f.foo(1) == 1
    assert Foo.foo.__qualname__ in registry
    assert registry[Foo.foo.__qualname__](f, 1) == 1

    assert foo(1) == 1
    assert foo.__qualname__ in registry
    assert registry[foo.__qualname__](1) == 1

