#!/usr/bin/env python
import sys
import os
import argparse
import asyncio
from genesynth.orchestration import *

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', required=True, help='schema file')
parser.add_argument('-o', '--output', help='output filename if given. defaults to input filename without extension')
parser.add_argument('--stdout', action='store_true', help='DEPRECATED print output to stdout')

def main(filename, output=None):
    pipe = Orchestration.read_config(filename)
    pipe.run()
    if output is None:
        asyncio.run(pipe.root.save())
        with open(pipe.root._file) as fh:
            for line in fh:
                sys.stdout.write(line)
    else:
        asyncio.run(pipe.root.save(output))

if __name__ == '__main__':
    args = parser.parse_args()
    main(args.filename, args.output)
