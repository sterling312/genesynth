import logging
import numpy as np
from scipy import stats

def mask(arr, value):
    return np.where(arr==value)[0]

def index_value(arr):
    unique = np.unique(arr)
    size = arr.size
    index = {}
    for val in unique:
        m = mask(arr, val)
        size -= m.size
        index[val] = m
    assert size == 0, f'number of index has {size} element less than original'
    return index

