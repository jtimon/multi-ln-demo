FROM ubuntu:18.04

RUN apt-get -yqq update \
  && apt-get install -qfy \
    python3 \
    python3-pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

COPY py-ln-gateway/requirements.txt /wd/py-ln-gateway/requirements.txt
RUN pip3 install -r /wd/py-ln-gateway/requirements.txt --require-hashes
COPY py-ln-gateway /wd/py-ln-gateway
RUN cd /wd/py-ln-gateway && python3 setup.py install

COPY docker/py-gateway.Procfile /wd/docker/py-gateway.Procfile
COPY docker/entrypoint-py-gateway.sh /wd/docker/entrypoint-py-gateway.sh

COPY conf/bob_gateway.json /wd/conf/bob_gateway.json
COPY conf/carol_gateway.json /wd/conf/carol_gateway.json
