FROM ubuntu:18.04

RUN apt-get -yqq update \
  && apt-get install -qfy \
    curl \
    libsodium-dev \
    python3 \
    python3-pip \
    xz-utils \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

COPY docker/honcho-requirements.txt /wd/honcho-requirements.txt
RUN pip3 install -r honcho-requirements.txt --require-hashes

# TODO remove everything except /wd/bitcoin-0.19.0.1/bin/bitcoin-cli
# This is only needed for bitcoin-cli for lightning
ENV SHA256SUM_BITCOINCORE=732cc96ae2e5e25603edf76b8c8af976fe518dd925f7e674710c6c8ee5189204
RUN curl -sL -o bitcoin.tar.gz https://bitcoincore.org/bin/bitcoin-core-0.19.0.1/bitcoin-0.19.0.1-x86_64-linux-gnu.tar.gz \
 && echo "${SHA256SUM_BITCOINCORE}  bitcoin.tar.gz" | sha256sum --check \
 && tar xzf bitcoin.tar.gz -C /wd \
 && rm bitcoin.tar.gz
ENV PATH="/wd/bitcoin-0.19.0.1/bin:${PATH}"

ENV SHA256SUM_CLIGHTNING=baf33d33ebe588bb1dc97fdd39390f8868515baaa8a7559dee4407ab04f5bc39
RUN curl -sL -o lighting.tar.gz https://github.com/ElementsProject/lightning/releases/download/v0.7.2.1/clightning-v0.7.2.1-Ubuntu-18.04.tar.gz \
 && echo "${SHA256SUM_CLIGHTNING}  lighting.tar.gz" | sha256sum --check \
 && ls \
 && tar xf lighting.tar.gz -C /wd \
 && rm /wd/usr/bin/lightning-cli \
 && rm -r /wd/usr/share \
 && rm lighting.tar.gz
ENV PATH="/wd/usr/bin:${PATH}"

COPY conf /wd/conf
COPY docker/clightning /wd/docker/clightning
