"""
Mat contains all matrix and masking operations that meets the constraint needs.
"""

import logging
import numpy as np
from scipy import stats
from scipy import signal
import matplotlib.pyplot as plt

def mask(arr, value):
    return np.where(arr==value)[0]

def null_percent(size, percent=0):
    return np.random.binomial(1, percent/100., size) == 1

def ordered_index(arr):
    return np.argsort(arr)

def indexed(arr, idx):
    return arr[idx]

def incremental_index(arr):
    return np.argsort(ordered_index(arr))

def fitted_model(arr, dist=stats.norm):
    return dist(*dist.fit(arr)) 

def kernel(arr, confidence_level: float = 0.9999, dist=stats.norm):
    n = arr.size
    m = fitted_model(arr, dist)
    mu, var = m.stats('mv')
    sig = var**0.5
    low, high = m.interval(confidence_level)
    z = (high - low) / sig
    index = np.linspace(low, high, n + 1)
    g = m.pdf(index)
    return g / (m.cdf(high) - m.cdf(low))
    #return g/g.sum()

def bootstrap(arr, statistic=np.median, confidence_level=0.95, method='BCa'):
    return stats.bootstrap((arr,), statistic, confidence_level=confidence_level, method=method)

def gkernel(n: int, sig: float):
    k = signal.windows.gaussian(n, sig)
    return k/k.sum()

def gaussian_smooth(arr, sig):
    k = gkernel(arr.size + 1, sig)
    # TODO double check off by one error
    start = int(arr.size/2)
    return signal.fftconvolve(arr, k)[start: arr.size]

def bootstrapped_gaussian_smooth(arr, confidence_level=0.95):
    b = bootstrap(arr, np.std, confidence_level=confidence_level)
    sig_low = b.confidence_interval.low
    sig_high = b.confidence_interval.high
    return gaussian_smooth(arr, sig_low), gaussian_smooth(arr, sig_high)
