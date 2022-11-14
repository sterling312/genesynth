import pytest
from pytest import fixture
import numpy as np
from genesynth.types import reseed
from genesynth.mat import *

@fixture(scope='function')
def arr():
    reseed(1)
    arr = np.random.randint(0, 10, 10)
    # array([5, 8, 9, 5, 0, 0, 1, 7, 6, 9]
    yield arr

def test_mask(arr):
    value = mask(arr, 9)
    np.testing.assert_array_almost_equal(value, [2, 9])

def test_null_percent(arr):
    mask = null_percent(arr.size, 50)
    assert mask.sum() == 5
    np.testing.assert_array_equal(mask.data, [True, False, True, False, True, False, True, False, True, False])

def test_indexed(arr):
    idx = np.random.randint(0, 10, 10)
    array = indexed(arr, idx)
    np.testing.assert_array_equal(array, [9, 0, 0, 9, 0, 9, 0, 7, 7, 9])

def test_ordered_index(arr):
    idx = ordered_index(arr)
    np.testing.assert_array_equal(idx, [4, 5, 6, 0, 3, 8, 7, 1, 2, 9])

def test_incremental_index(arr):
    idx = incremental_index(arr)
    np.testing.assert_array_equal(idx, [3, 7, 8, 4, 0, 1, 2, 6, 5, 9])
