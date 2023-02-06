import pytest
import os
from pytest import fixture
from click.testing import CliRunner
from genesynth.cli import *

def test_run_out():
    run('tests/test.yaml', 'tests/out')
    assert os.path.isfile('tests/out')
    os.remove('tests/out')

def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ['--filename', 'tests/test.yaml', '--output', 'tests/out'])
    assert result.exit_code == 0
    assert os.path.isfile('tests/out')
    os.remove('tests/out')
