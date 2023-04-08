.PHONY: build
build:
	docker build -t genesynth .

.PHONY: run
run:
	docker run -it --rm -v $$(pwd):/home genesynth python -m genesynth.cli --filename /home/tests/e_commerce.yaml --stdout
