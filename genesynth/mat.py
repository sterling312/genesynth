"""
Mat contains all matrix and masking operations that meets the constraint needs.
"""

import logging
import numpy as np
from scipy import stats

def mask(arr: np.array, value):
    """return index of input value against the array
    length of the array depends on number matches
    """
    return np.where(arr==value)[0]

def null_percent(size: int, percent: float = 0.):
    """return masking array for null value.
    """
    return np.random.binomial(1, percent/100., size) == 1

def ordered_index(arr):
    """return index to sort array in incremental order
    """
    return np.argsort(arr, kind='stable')

def indexed(arr, idx):
    """return array with index applied
    """
    return arr[idx]

def revert_ordered_index(arr):
    """return index to unsort array
    """
    return np.argsort(ordered_index(arr), kind='stable')
