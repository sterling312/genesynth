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

def identity(size: int, matmul=False):
    """return index array that will produce identical array
    when applied to the original array
    if matmul is true, it will return boolean array
        otherwise it will return index array
    """
    if matmul:
        return np.ones(size).astype(bool)
    return np.arange(size)

def unique(arr: np.array):
    """return subarray of unique values
    """
    return np.unique(arr)

def sample(size: int, options, replace=True):
    """return sampled value from options
    if options is a dict, sampling probability distribution will be 
        generated from normalizing the value from options, otherwise 
        it will be a uniform distribution iterated over options
    """
    if isinstance(options, dict):
        p = np.array(list(options.values()))
        p = p / p.sum()
        options = list(options)
    else:
        p = None
    return np.random.choice(options, size, replace=replace, p=p)

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
    """return masking array for null value drawn from a binomial distribution.
    """
    return np.random.binomial(1, percent/100., size) == 1

def nullable(arr, percent=0, mask=None, null=''):
    """return masked array with null being the fill_value
    make sure that null value matches the datatype of array, or it will error
    use arr.filled() to return array with mask filled
    """
    if mask is None:
        return np.ma.MaskedArray(arr, mask=null_percent(arr.size, percent), fill_value=null)
    else:
        return np.ma.MaskedArray(arr, mask=mask, fill_value=null)

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
    if isinstance(model, str):
        return StatsModel[model].value(*args, **kwargs)
    else:
        return StatsModel(model).value(*args, **kwargs)

def stats_model_generate(size: int, min: float, max: float, *args, model: str = 'uniform', unique=False, **kwargs):
    """return array based on the statistical distribution
       parameters to the model can be passed in as ordered or key-word wildcards 
    """
    if model == 'uniform':
        m = stats_model(min, max, *args, model=model)
    else:
        m = stats_model(*args, model=model, **kwargs)
    p99_low, p99_high = m.interval(0.99)
    p_low, p_high = m.cdf(min), m.cdf(max)
    if unique:
        p = np.linspace(p_low, p_high, size)
    else:
        p = np.random.rand(size) * (p_high - p_low) + p_low
    return m.ppf(p)

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
