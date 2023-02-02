import pytest
import os
from pytest import fixture
from genesynth.cli import *

def test_run_out():
    run('tests/test.yaml', 'tests/out')
    assert os.path.isfile('tests/out')
