FROM ubuntu:18.04

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
    python \
    python-pip \
    python3 \
    tor \
    zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

COPY docker/requirements.txt /wd/requirements.txt
RUN pip install -r requirements.txt --require-hashes

COPY docker/build-daemon.sh /wd/build-daemon.sh
# Build custom daemon able to produce and support an arbitrary number of chains
ENV DAEMON_NAME=bitcoin
ENV BRANCH_COMMIT=0.13-new-testchain
ENV REPO_HOST=https://github.com/jtimon
ENV REPO_NAME=bitcoin
RUN bash build-daemon.sh $BRANCH_COMMIT $REPO_NAME $REPO_HOST $DAEMON_NAME
ENV PATH="/wd/$REPO_NAME/src:${PATH}"

COPY docker/build-clightning.sh /wd/build-clightning.sh
ENV LN_BRANCH_COMMIT=custom-chain
ENV LN_REPO_HOST=https://github.com/jtimon
ENV LN_REPO_NAME=lightning
RUN bash build-clightning.sh $LN_BRANCH_COMMIT $LN_REPO_NAME $LN_REPO_HOST
ENV PATH="/wd/$LN_REPO_NAME/lightningd:${PATH}"

COPY docker/daemons.env /wd/daemons.env
COPY docker/daemons.proc /wd/daemons.proc
COPY docker/daemon-conf /wd/conf
COPY docker/lightningd-conf /wd/ln-conf
CMD honcho start -e daemons.env -f daemons.proc
