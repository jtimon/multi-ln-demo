FROM ubuntu:18.04

RUN apt-get -yqq update \
  && apt-get install -qfy \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

ENV SHA256SUM_CLIGHTNING=baf33d33ebe588bb1dc97fdd39390f8868515baaa8a7559dee4407ab04f5bc39
RUN curl -sL -o lighting.tar.gz https://github.com/ElementsProject/lightning/releases/download/v0.7.2.1/clightning-v0.7.2.1-Ubuntu-18.04.tar.gz
 && echo "${SHA256SUM_CLIGHTNING}  lighting.tar.gz" | sha256sum --check \
 && tar xzf lighting.tar.gz -C /wd \
 && rm lighting.tar.gz \
# TODO remove more files
ENV PATH="/wd/usr/local/bin:${PATH}"

COPY conf /wd/conf
COPY docker /wd/docker
