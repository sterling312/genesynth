"""
Extensions is used for user defined types and allows the library to reference it during type conversion.
"""
from collections import ChainMap
from genesynth.types import types, Datatypes

extensions = Datatypes()  

datatypes = ChainMap(types, extensions)
