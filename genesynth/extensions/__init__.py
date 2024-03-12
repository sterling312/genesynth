"""
Extensions is used for user defined types and allows the library to reference it during type conversion.
"""
import os
import glob
import importlib
from collections import ChainMap
from genesynth.types import types, Datatypes

extensions = Datatypes()  

datatypes = ChainMap(types, extensions)

for module in glob.glob(f'{os.path.dirname(__file__)}/*'):
    module, ext = os.path.splitext(os.path.basename(module))
    if ext == '.py':
        importlib.import_module(f'{__package__}.{module}')
