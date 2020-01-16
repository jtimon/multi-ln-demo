FROM ubuntu:18.04

# TODO don't use ppa:bitcoin for libdb4.8++
RUN apt-get -yqq update \
  && apt-get install -y software-properties-common \
  && add-apt-repository ppa:bitcoin/bitcoin \
  && apt-get update \
  && apt-get install -qfy \
    automake \
    autotools-dev \
    bsdmainutils \
    build-essential \
    curl \
    git \
    libboost-chrono-dev \
    libboost-filesystem-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-test-dev \
    libboost-thread-dev \
    libdb4.8++-dev \
    libdb4.8-dev \
    libevent-dev \
    libminiupnpc-dev \
    libtool \
    libzmq3-dev \
    make \
    pkg-config \
    python3 \
    python3-pip \
    tor \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

COPY docker/build-daemon.sh /wd/build-daemon.sh
# Build custom daemon able to produce and support an arbitrary number of chains
# This corresponds to https://github.com/bitcoin/bitcoin/pull/17037
ENV DAEMON_NAME=bitcoin
ENV BRANCH_COMMIT=demo-multiln-6
ENV REPO_HOST=https://github.com/jtimon
ENV REPO_NAME=bitcoin
RUN bash build-daemon.sh $BRANCH_COMMIT $REPO_NAME $REPO_HOST $DAEMON_NAME
ENV PATH="/wd/$REPO_NAME/src:${PATH}"

COPY docker/honcho-requirements.txt /wd/honcho-requirements.txt
RUN pip3 install -r honcho-requirements.txt --require-hashes

COPY conf/bitcoind.conf /wd/conf/bitcoind.conf
COPY docker/entrypoint-bitcoind.sh /wd/docker/entrypoint-bitcoind.sh
COPY docker/regtest/bitcoind.Procfile /wd/docker/regtest/bitcoind.Procfile
COPY docker/2-chains/bitcoind.Procfile /wd/docker/2-chains/bitcoind.Procfile
COPY docker/3-chains/bitcoind.Procfile /wd/docker/3-chains/bitcoind.Procfile
