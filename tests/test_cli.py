import pytest
from pytest import fixture
from genesynth.cli import *

def test_test():
    run('tests/test.yaml')
