ARG VERSION=3.11
FROM python:${VERSION}

ADD requirements.txt /tmp/
RUN python -m pip install -r /tmp/requirements.txt

WORKDIR /home
RUN mkdir -p /tmp/genesynth
ADD . /tmp/genesynth/
RUN cd /tmp/genesynth && python setup.py install && rm -rf /tmp/genesynth

EXPOSE 8080
RUN adduser genesynth 

USER genesynth

ENTRYPOINT ["python", "-m"]
CMD ["genesynth.server", "--host=0.0.0.0"]
