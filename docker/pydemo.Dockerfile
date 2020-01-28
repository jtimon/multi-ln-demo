FROM ubuntu:18.04

RUN apt-get -yqq update \
  && apt-get install -qfy \
    python3 \
    python3-pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

COPY docker/requirements.txt /wd/requirements.txt
RUN pip3 install -r requirements.txt --require-hashes
COPY multiln /wd/multiln
COPY setup.py /wd/setup.py
RUN python3 /wd/setup.py install
