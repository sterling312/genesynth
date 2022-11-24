"""
Constraints that governs the relationship between types.
Constraints will govern the following:
Node Level:
    - binds types of different types (swich between type class)
    - default parameter translation
    - masking and sampling
    - ordering
    - *data validation (this will not be provided out of the box)
Edge Level:
    - processing order of operations during orchestration
    - foreign relationship to determine order of operations
"""
import enum
from genesynth.mat import mask, null_percent, ordered_index, incremental_index

class Builtin(enum.Enum):
    unique = 1 
    notnull = 2
    incremental = 3
    uuid = 4

class Constraints(enum.Enum):
    ONEOF = 'oneOf'
    SUBSET = 'subset'
    UNIQUE = 'unique'
    NOTNULL = 'notnull'
    UUID = 'uuid'
    REGEXP = 'regexp'
    FORMAT = 'format'
    INCREMENTAL = 'incremental'
    BETWEEN = 'between'

class NodeConstraint:
    pass

class EdgeConstraint:
    pass
