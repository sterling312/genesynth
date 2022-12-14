import pytest
from pytest import fixture
import asyncio
from genesynth.types import *

@fixture(scope='function')
def params():
    reseed(1)
    yield {
            'name': 'name',
            'size': 10,
    }

def test_integer(params):
    n = IntegerFixture(min=0, max=100, **params)
    arr = np.array([37, 12, 72, 9, 75, 5, 79, 64, 16, 1])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_serial(params):
    n = SerialFixture(min=0, step=2, **params)
    arr = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_boolean(params):
    n = BooleanFixture(**params)
    arr = np.array([True, True, False, False, True, True, True, True, True, False])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_float(params):
    n = FloatFixture(min=0, max=10, **params)
    arr = np.array([4.170220, 7.203245, 0.001143748, 3.023326, 1.467559, 0.9233859, 1.862602, 3.455607, 3.967675, 5.388167])
    np.testing.assert_array_almost_equal(asyncio.run(n.generate()), arr)

def test_decimal(params):
    n = DecimalFixture(min=0, max=10, precision=0, scale=5, **params)
    arr = np.array([4.17022, 7.20324, 0.00114, 3.02333, 1.46756, 0.92339, 1.8626, 3.45561, 3.96767, 5.38817])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_text(params):
    n = BaseTextFixture(length=5, **params)
    arr = np.array(['JXdhV', '5z45g', 'OLTx1', 'DbxAl', 'ecikH', 'AhkoU', 'msHd1', 'spUal', 'kFqgK', '7MvZh'])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_string(params):
    n = StringFixture(subtype='person', field='first_name', **params)
    arr = np.array(['Walter', 'Hershel', 'Rudolf', 'Shirl', 'Jackeline', 'Ron', 'Martin', 'Afton', 'Keren', 'Zackary'])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_map(params):
    children = {
        'id': SerialFixture(name='id', size=params['size'], min=0, step=1),
        'value': IntegerFixture(name='value', size=params['size'], min=0, max=10),
    }
    n = BaseMapFixture(children=children, **params)
    records = asyncio.run(n.generate())
    assert len(records) == len(children)
    assert set(records) == {'id', 'value'}
    np.testing.assert_array_equal(records['id'], np.arange(10))

def test_array(params):
    children = [
        SerialFixture(name='id', size=params['size'], min=0, step=1),
        IntegerFixture(name='value', size=params['size'], min=0, max=10),
    ]
    n = BaseArrayFixture(children=children, **params)
    records = asyncio.run(n.generate())
    assert len(records) == len(children)
    np.testing.assert_array_equal(records[0], np.arange(10))

def test_nest(params):
    fields = {
        'value': IntegerFixture(name='value', size=params['size'], min=0, max=10),
    }
    children = {
        'id': SerialFixture(name='id', size=params['size'], min=0, step=1),
        'json': BaseMapFixture(name='json', size=params['size'], children=fields),
    }
    n = BaseMapFixture(children=children, **params)
    records = asyncio.run(n.generate())
    assert set(records) == {'id', 'json'}
    np.testing.assert_array_equal(records['id'], np.arange(10))
    assert set(records['json']) == {'value'}
    np.testing.assert_array_equal(records['json']['value'], np.array([5, 8, 9, 5, 0, 0, 1, 7, 6, 9]))
