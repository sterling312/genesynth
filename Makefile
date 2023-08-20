PORT=8080

.PHONY: build
build:
	docker build -t genesynth .

.PHONY: run
run: build
	docker run -it --rm -p ${PORT}:8080 genesynth
