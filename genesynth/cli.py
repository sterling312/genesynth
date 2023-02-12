#!/usr/bin/env python
import os
import argparse
import asyncio
from genesynth.orchestration import *

parser = argparse.ArgumentParser()
parser.add_argument('--filename', required=True, help='filename')
parser.add_argument('--output', help='filename')

def main(filename, output=None):
    if output is None:
        output, ext = os.path.splitext(os.path.basename(filename))
    pipe = Orchestration.read_yaml(filename)
    pipe.run()
    root = pipe.graph.root.pop()
    asyncio.run(root.save(output))

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.filename, args.output)
