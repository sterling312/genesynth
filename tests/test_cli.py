import pytest
import os
from pytest import fixture
from genesynth.orchestration import *
from genesynth.cli import *

@fixture
def filename():
    reseed(1)
    return 'tests/test.yaml'

@fixture
def test_main(filename='tests/test.yaml'):
    main(filename, 'tests/out')
    assert os.path.isfile('tests/out')
    os.remove('tests/out')

