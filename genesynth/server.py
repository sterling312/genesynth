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
    size = request.query.get('size')
    schema = await request.json()
    pipe = Orchestration.read_dict(schema, size=size)
    pipe.run()
    await pipe.root.save() 
    with open(pipe.root._file) as fh:
        try:
            data = [json.loads(line) for line in fh if line.strip()]
        except:
            fh.seek(0)
            data = [line for line in fh if line.strip()]
        del pipe
        return web.json_response(data)

if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
