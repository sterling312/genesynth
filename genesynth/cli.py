#!/usr/bin/env python
import os
import asyncio
import click
from genesynth.orchestration import *

def run(filename, output=None):
    if output is None:
        output, ext = os.path.splitext(os.path.basename(filename))
    pipe = Orchestration.read_yaml(filename)
    pipe.run()
    root = pipe.graph.root.pop()
    asyncio.run(root.save(output))

@click.command()
@click.option('--filename', help='filename')
@click.option('--output', default=None, help='output file')
def main(filename, output):
    run(filename, output)

if __name__ == '__main__':
    main()
