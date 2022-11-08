import logging
import numpy as np
from scipy import stats

def mask(arr, value):
    return np.where(arr==value)[0]

def null_percent(size, percent=0):
    return np.random.binomial(1, percent/100., size) == 1

def ordered_index(arr):
    return np.argsort(arr)

def incremental_index(arr):
    return np.argsort(ordered_index(arr))
