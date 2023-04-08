ARG VERSION=3.10
FROM python:${VERSION}

ADD requirements.txt /tmp/
RUN python -m pip install -r /tmp/requirements.txt
ADD dev-requirements.txt /tmp/
RUN python -m pip install -r /tmp/dev-requirements.txt

WORKDIR /home
RUN mkdir -p /tmp/genesynth
ADD . /tmp/genesynth/
RUN cd /tmp/genesynth && python setup.py install
