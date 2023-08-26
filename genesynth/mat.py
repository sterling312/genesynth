"""
Mat contains all matrix and masking operations that meets the constraint needs.
"""

import logging
import enum
import numpy as np
from scipy import stats

class StatsModel(enum.Enum):
    uniform = stats.uniform
    normal = stats.norm
    student_t = stats.t
    binomial = stats.binom
    poisson = stats.poisson
    alpha = stats.alpha
    beta = stats.beta
    gamma = stats.gamma
    cosine = stats.cosine
    fisher = stats.f
    power_law = stats.powerlaw
    bootstrap = stats.bootstrap

def mask(arr: np.array, low, high=None):
    """return index of input value against the array
    length of the array depends on number matches
    """
    if high is not None:
        return np.where((arr>=low) & (arr<high))[0]
    else:
        return np.where(arr==low)[0]

def mask_index(arr: np.array, low, high=None):
    """return masking index for value that matches
    """
    if high is not None:
        return np.where((arr>=low) & (arr<high), True, False)
    else:
        return np.where(arr==low, True, False)

def null_percent(size: int, percent: float = 0.):
    """return masking array for null value.
    """
    return np.random.binomial(1, percent/100., size) == 1

def ordered_index(arr: np.array):
    """return index to sort array in incremental order
    """
    return np.argsort(arr, kind='stable')

def indexed(arr: np.array, idx: np.array):
    """return array with index applied
    """
    return arr[idx]

def revert_ordered_index(arr: np.array):
    """return index to unsort array
    """
    return np.argsort(ordered_index(arr), kind='stable')

def cosine_similarity(a: np.array, b: np.array):
    """return cosine similarity between two arrays
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def stats_model(*args, model: str = 'uniform', **kwargs):
    """return stats model based on input parameters
       model supported are:
            alpha
            beta
            binomial
            cosine
            fisher
            gamma
            normal
            poisson
            power_law
            student_t
            uniform
       parameters to the model can be passed in as ordered or key-word wildcards 
    """
    return StatsModel[model].value(*args, **kwargs)

def stats_model_generate(size: int, *args, model: str = 'uniform', **kwargs):
    """return array based on the statistical distribution
       parameters to the model can be passed in as ordered or key-word wildcards 
    """
    return stats_model(*args, model=model, **kwargs).rvs(size)

def stats_model_fit(arr: np.array, model: str = 'uniform'):
    """return model best fit parameters based on input array
       model supported are:
            alpha
            beta
            cosine
            fisher
            gamma
            normal
            power_law
            student_t
            uniform
       parameters to the model can be passed in as ordered or key-word wildcards 
    """
    return StatsModel[model].value.fit(arr)
