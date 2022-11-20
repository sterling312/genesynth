import enum
from genesynth.types import Datatypes

extensions = Datatypes()  

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
