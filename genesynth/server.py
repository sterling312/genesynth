#!/usr/bin/env python
import sys
import os
import json
import argparse
import asyncio
from aiohttp import web
from genesynth.orchestration import *

parser = argparse.ArgumentParser()
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
