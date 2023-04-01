import pytest
from pytest import fixture
import asyncio
import networkx as nx
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

def test_password(params):
    n = BcryptPassword(**params)
    arr = np.array(['$2b$12$i0VpEBOWfbZAVaBSo63bbH6xnAbnBEoonCrbZINl91huSS6AZPsK2',
                    '$2b$12$0FKcpXzkIRPxBFWGyEbcR8KykF8VH1oF7JCqH7aWY2TYGIAd1JmFE',
                    '$2b$12$wvHMLCbokK1XXYp0PfbaUpgMvejGkqSCtDbxAlg3FmLYbbjSjRQHn',
                    '$2b$12$8XGnOyJtNds82s1t6Uzpa2cY7Jk18RFxvmPAmgPsEu23bmu9WvnPZ',
                    '$2b$12$5v2QE9oSfk4nVL0wvs1L73iIgce1WZvMWxJnfq3I5CrWZaPfh2co9',
                    '$2b$12$AhkoUg4x84spDgOca8sKBtd488gnM8HQPqHtpfr8BON6ytut03suH',
                    '$2b$12$JKpbpeIeeNsXE1jFXe6kW9YtgF5s3i4bt3X40UQlAjSPpd7YIH0Cy',
                    '$2b$12$upbOzJdwihqZyyLoaGFOBQToEDnzI44rOceF2jV2tQ0xRTK137Jkp',
                    '$2b$12$nJUdQSvFkTc8YMq47iW0ORB58xXAkuh47hLzhspUalBbMLZmrHqKp',
                    '$2b$12$QXY8HE1VJxrgYhUH7V8iFJtFwGaBBsyWQEOxmarL2ZF9CZzU9skMG'])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_timestamp(params):
    n = BaseTimestamp(min='2020-01-01', max='2020-01-10', **params)
    arr = np.array([datetime(2020,1,1), datetime(2020,1,2), datetime(2020,1,3), datetime(2020,1,4), datetime(2020,1,5), datetime(2020,1,6), datetime(2020,1,7), datetime(2020,1,8), datetime(2020,1,9), datetime(2020,1,10)])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_date(params):
    n = BaseDate(min='2020-01-01', max='2020-01-10', **params)
    arr = np.array([date(2020,1,1), date(2020,1,2), date(2020,1,3), date(2020,1,4), date(2020,1,5), date(2020,1,6), date(2020,1,7), date(2020,1,8), date(2020,1,9), date(2020,1,10)])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_time(params):
    n = BaseTime(min=time(0), max=time(23, 59, 59), **params)
    arr = np.array([time(0), time(2, 39, 59, 888888), time(5, 19, 59, 777777), time(7, 59, 59, 666666), time(10, 39, 59, 555555), time(13, 19, 59, 444444), time(15, 59, 59, 333333), time(18, 39, 59, 222222), time(21, 19, 59, 111111), time(23, 59, 59)])
    np.testing.assert_array_equal(asyncio.run(n.generate()), arr)

def test_foreign(params):
    parent = IntegerFixture(min=0, max=100, name='parent', size=params['size'])
    child = IntegerFixture(min=0, max=100, name='parent.child', size=params['size'])
    G = nx.DiGraph()
    G.add_edge(parent, child)
    n = BaseForeign.from_params(graph=G, depends_on='parent.child', **params)
    arr = np.array([37, 12, 72, 9, 75, 5, 79, 64, 16, 1])
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
