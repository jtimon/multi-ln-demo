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

# TODO install pylightning in a simpler way
COPY docker/build-clightning.sh /wd/build-clightning.sh
ENV LN_BRANCH_COMMIT=v0.7.2.1-demo-3
ENV LN_REPO_HOST=https://github.com/jtimon
ENV LN_REPO_NAME=lightning
RUN bash build-clightning.sh $LN_BRANCH_COMMIT $LN_REPO_NAME $LN_REPO_HOST
ENV PATH="/wd/$LN_REPO_NAME/lightningd:${PATH}"

RUN cd /wd/$LN_REPO_NAME/contrib/pylightning && \
    python3 setup.py develop

COPY py-ln-gateway/requirements.txt /wd/py-ln-gateway/requirements.txt
RUN pip install -r /wd/py-ln-gateway/requirements.txt --require-hashes
COPY py-ln-gateway /wd/py-ln-gateway
RUN cd /wd/py-ln-gateway && python setup.py install

COPY docker/py-gateway.Procfile /wd/docker/py-gateway.Procfile
COPY docker/entrypoint-py-gateway.sh /wd/docker/entrypoint-py-gateway.sh
