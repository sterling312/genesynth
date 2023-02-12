import pytest
import os
from pytest import fixture
from genesynth.cli import *

def test_main():
    main('tests/test.yaml', 'tests/out')
    assert os.path.isfile('tests/out')
    os.remove('tests/out')

