PORT=8080
FILENAME=

.PHONY: build
build:
	docker build -t genesynth .

.PHONY: run
run: build
	docker run -it --rm --name genesynth -p ${PORT}:8080 genesynth

.PHONY: cli
cli: ${FILENAME} build
	docker run -it --rm -v ${FILENAME}:/tmp/input.yaml genesynth genesynth.cli -f /tmp/input.yaml --stdout

.PHONY: test
test:
	pytest -vv tests

.PHONY: twine
twine:
	rm -rf dist
	python setup.py bdist_wheel sdist
	python -m twine upload -r genesynth --verbose dist/*
