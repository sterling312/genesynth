[![Python packages](https://github.com/sterling312/genesynth/actions/workflows/github-actions-unittests.yaml/badge.svg)](https://github.com/sterling312/genesynth/actions/workflows/github-actions-unittests.yaml)

# genesynth
This library is used to synthetically generate structured data based on configuration to be used for testing as well as structured data training purposes. The approach of the library is to leverage as much as C-level python packages such as numpy and scipy to generate data at field level, one type at a time, and use graph approach to piece together the complex dependency as well as de-normalization/sampling from each fields to construct data in a scalable manner fast.


# install
```
pip install genesynth
```

# example
```
$ python -m genesynth.server --host=0.0.0.0 -p 8080
```
```
$ make run
```

```
$ python -m genesynth.cli -f tests/test.yaml --stdout
```
```
$ make cli FILENAME=$(pwd)/tests/test.yaml
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
* GenAI based field-level data generation (ollama & openai)

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
