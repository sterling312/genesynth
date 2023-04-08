ARG VERSION=3.10
FROM python:${VERSION}

ADD requirements.txt /tmp/
RUN python -m pip install -r /tmp/requirements.txt
ADD dev-requirements.txt /tmp/
RUN python -m pip install -r /tmp/dev-requirements.txt

WORKDIR /home
RUN mkdir -p /home/genesynth
ADD . /home/genesynth/
RUN cd genesynth && python setup.py install
