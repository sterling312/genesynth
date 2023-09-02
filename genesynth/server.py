#!/usr/bin/env python
import sys
import os
import json
import logging
import argparse
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from genesynth.orchestration import *
from genesynth.utils import clean_text

parser = argparse.ArgumentParser()
parser.add_argument('--host', default='localhost', help='server host')
parser.add_argument('-p', '--port', default=8080, type=int, help='server port')
parser.add_argument('-l', '--level', default='INFO', help='log level')

logger = logging.getLogger(__name__)
app = FastAPI()

class Schema(BaseModel):
    type: str = 'json'
    metadata: dict = {}
    constraints: list = []
    properties: dict = {}

@app.get('/')
async def home():
    return {'status': 'OK'}

@app.post('/api')
async def api(schema: Schema, size=None, string=False):
    pipe = Orchestration.read_dict(dict(schema), size=size)
    pipe.run()
    await pipe.root.save() 
    with open(pipe.root._file) as fh:
        try:
            if string:
                data = [json.loads(line) for line in fh if line.strip()]
            else:
                data = [json.loads(clean_text(line)) for line in fh if line.strip()]
        except:
            fh.seek(0)
            if string:
                data = [line for line in fh if line.strip()]
            else:
                data = [clean_text(line) for line in fh if line.strip()]
        del pipe
        return data

def run_server(host='localhost', port=8080, level='INFO'):
    debug = level == 'DEBUG'
    logging.basicConfig(level=level)
    uvicorn.run('__main__:app', host=host, port=port, log_level=level.lower(), reload=debug)

if __name__ == '__main__':
    args = parser.parse_args()
    run_server(host=args.host, port=args.port, level=args.level)
