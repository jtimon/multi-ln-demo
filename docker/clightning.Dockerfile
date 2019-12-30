FROM ubuntu:18.04

# TODO cleaunup dependencies
RUN apt-get -yqq update \
  && apt-get install -y software-properties-common \
  && add-apt-repository ppa:bitcoin/bitcoin \
  && apt-get update \
  && apt-get install -qfy \
    autoconf \
    automake \
    autotools-dev \
    bsdmainutils \
    build-essential \
    curl \
    gettext \
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
    libgmp-dev \
    libminiupnpc-dev \
    libsodium-dev \
    libsqlite3-dev \
    libssl-dev \
    libtool \
    libzmq3-dev \
    make \
    net-tools \
    pkg-config \
    python3 \
    python3-distutils \
    python3-mako \
    python3-pip \
    tor \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

RUN ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip

# TODO Remove this, only needed for the cli for lightning
COPY docker/build-daemon.sh /wd/build-daemon.sh
# Build custom daemon able to produce and support an arbitrary number of chains
# This corresponds to https://github.com/bitcoin/bitcoin/pull/17037
ENV DAEMON_NAME=bitcoin
ENV BRANCH_COMMIT=demo-multiln-6
ENV REPO_HOST=https://github.com/jtimon
ENV REPO_NAME=bitcoin
RUN bash build-daemon.sh $BRANCH_COMMIT $REPO_NAME $REPO_HOST $DAEMON_NAME
ENV PATH="/wd/$REPO_NAME/src:${PATH}"

COPY docker/build-clightning.sh /wd/build-clightning.sh
ENV LN_BRANCH_COMMIT=v0.7.2.1-demo-3
ENV LN_REPO_HOST=https://github.com/jtimon
ENV LN_REPO_NAME=lightning
RUN bash build-clightning.sh $LN_BRANCH_COMMIT $LN_REPO_NAME $LN_REPO_HOST
ENV PATH="/wd/$LN_REPO_NAME/lightningd:${PATH}"

COPY docker/honcho-requirements.txt /wd/honcho-requirements.txt
RUN pip3 install -r honcho-requirements.txt --require-hashes

COPY conf /wd/conf
COPY docker /wd/docker
