import pytest
import os
from pytest import fixture
from genesynth.cli import *

def test_test():
    run('tests/test.yaml', 'tests/out')
    assert os.path.isfile('tests/out')
