[![Python packages](https://github.com/sterling312/genesynth/actions/workflows/github-actions-unittests.yaml/badge.svg)](https://github.com/sterling312/genesynth/actions/workflows/github-actions-unittests.yaml)

# genesynth
Library to synthetically generate data for declarative data structures.

# install
```
pip install -r requirements.txt
```

# example
```
>>> from genesynth.orchestration import *
>>> pipe = Orchestration.read_yaml('tests/graph.yaml') 
>>> pipe.run()
>>> asyncio.run(pipe.root.save('graph.csv'))
```

# project status

## supported feature
* load yaml as configuration file
* arbitrary row size support
* data type mapping with configurable parameters
* JSON (semi-structured data) support
* improved data type support
* foreign relationship support
* DOT file graph
* table graph
* built-in orchestrator using graph
* thread and process support
* intermediary data temporary cache
* graph visualization

## key features to add
* add yaml validator
* fix header support
* additional output file formats (JSON, PSQL dump, CSV with quotes, etc)
* add support for JSON arrays
* improve constraint support
* add support for quoted string
* add support statistical distribution via kernel convolution
* optimize orchestration and disk cache efficiency
* optimize thread/process based generation
* convert serial to autoincrement constraint for integer type
* convert password to constraint of string type

## nice to have features to add
* support external scheduler
* support NLP based text generation
* support sklearn
* support integration with pytorch embedding
* support for object reference via $ref
* fix compatibility with [JSON schema array notation](https://json-schema.org/understanding-json-schema/reference/array.html#items)
* fix when json array child object appears as separate items
