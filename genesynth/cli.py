#!/usr/bin/env python
import click
from genesynth.orchestration import *

@click.command()
@click.option('--name', default='root', help='name of the model')
@click.option('--size', default=10, help='default size')
def main(name, size):
    pass

if __name__ == '__main__':
    pass
