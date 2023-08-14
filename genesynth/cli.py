#!/usr/bin/env python
import os
import argparse
import asyncio
from genesynth.orchestration import *

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', required=True, help='schema file')
parser.add_argument('-o', '--output', help='output filename if given. defaults to input filename without extension')
parser.add_argument('--stdout', action='store_true', help='print output to stdout')

def main(filename, output=None, stdout=False):
    if output is None:
        output, ext = os.path.splitext(os.path.basename(filename))
    pipe = Orchestration.read_yaml(filename)
    pipe.run()
    asyncio.run(pipe.root.save(output))
    if stdout:
        with open(output) as fh:
            print(fh.read())

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.filename, args.output, args.stdout)
