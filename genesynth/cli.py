#!/usr/bin/env python
import click
from genesynth.orchestration import *

def run(filename):
    pipe = Orchestration.read_yaml(filename)
    pipe.run()

@click.command()
@click.option('--filename', help='filename')
def main(filename):
    run(filename)

if __name__ == '__main__':
    main()
