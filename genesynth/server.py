#!/usr/bin/env python
import sys
import os
import json
import argparse
import asyncio
from aiohttp import web
from genesynth.orchestration import *

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--filename', required=True, help='schema file')
parser.add_argument('-o', '--output', help='output filename if given. defaults to input filename without extension')
parser.add_argument('--stdout', action='store_true', help='print output to stdout')

routes = web.RouteTableDef()

@routes.get('/')
async def home(request):
    return web.json_response({'status': 'OK'})

@routes.post('/api')
async def api(request):
    schema = await request.json()
    pipe = Orchestration.read_dict(schema)
    pipe.run()
    await pipe.root.save() 
    try:
        with open(pipe.root._file) as fh:
            data = [json.loads(line) for line in fh]
        return web.json_response(data)
    except:
        with open(pipe.root._file) as fh:
            data = fh.read()
        return web.Response(text=data)

if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
