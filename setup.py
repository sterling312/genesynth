#!/usr/bin/env python
import os
import importlib
import setuptools

name = 'genesynth'
version = importlib.import_module(f'{name}.version').__version__
description = f'Python package: {name}'

def readme(filename='README.md'):
    try:
        with open(filename) as fh:
            return fh.read()
    except:
        pass

def dep(filename='requirements.txt'):
    try:
        with open(filename) as fh:
            return [line.rstrip('\n') for line in fh]
    except:
        return []

if __name__ == '__main__':
    setuptools.setup(
        name=name,
        version=version,
        license='MIT',
        author='Gang Huang',
        description=description,
        long_description=readme(),
        long_description_content_type="text/x-rst",
        packages=setuptools.find_packages(),
        python_requires='>=3.9',
        install_requires=dep(),
    )
