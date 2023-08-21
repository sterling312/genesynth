PORT=8080
FILENAME=

.PHONY: build
build:
	docker build -t genesynth .

.PHONY: run
run: build
	docker run -it --rm -p ${PORT}:8080 genesynth

.PHONY: cli
cli: build
	docker run -it --rm -v ${FILENAME}:/tmp/input.yaml genesynth genesynth.cli -f /tmp/input.yaml --stdout

.PHONY: test
test:
	pytest -vv tests
