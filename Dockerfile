FROM ubuntu:18.10

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

# Install cargo for rust builds
RUN cd /root \
    && curl -s -L -O https://static.rust-lang.org/rustup.sh \
    && bash ./rustup.sh -y --verbose
ENV PATH="/root/.cargo/bin:${PATH}"

COPY docker/build-daemon.sh /wd/build-daemon.sh
# Build custom daemon able to produce and support an arbitrary number of chains
# This corresponds to https://github.com/bitcoin/bitcoin/pull/8994
ENV DAEMON_NAME=bitcoin
ENV BRANCH_COMMIT=demo-multiln-2
ENV REPO_HOST=https://github.com/jtimon
ENV REPO_NAME=bitcoin
RUN bash build-daemon.sh $BRANCH_COMMIT $REPO_NAME $REPO_HOST $DAEMON_NAME
ENV PATH="/wd/$REPO_NAME/src:${PATH}"

COPY docker/build-clightning.sh /wd/build-clightning.sh
# This corresponds to https://github.com/jtimon/lightning/pull/3
ENV LN_BRANCH_COMMIT=v0.7.2.1-5-chains
ENV LN_REPO_HOST=https://github.com/jtimon
ENV LN_REPO_NAME=lightning
RUN bash build-clightning.sh $LN_BRANCH_COMMIT $LN_REPO_NAME $LN_REPO_HOST
ENV PATH="/wd/$LN_REPO_NAME/lightningd:${PATH}"

RUN cd /wd/$LN_REPO_NAME/contrib/pylightning && \
    python3 setup.py develop

COPY rustdemo/Cargo.toml /wd/rustdemo/Cargo.toml
COPY rustdemo/src /wd/rustdemo/src
RUN cd /wd/rustdemo && \
    cargo test && \
    cargo build --release

COPY docker/requirements.txt /wd/requirements.txt
RUN pip install -r requirements.txt --require-hashes

COPY multiln /wd/multiln
COPY setup.py /wd/setup.py
RUN python /wd/setup.py install

COPY conf /wd/conf
COPY docker/daemons.env /wd/daemons.env
COPY docker/rustdemo-2-chains-entry-point.sh /wd/rustdemo-2-chains-entry-point.sh
COPY docker/rustdemo-2-chains-daemons.proc /wd/rustdemo-2-chains-daemons.proc
COPY docker/5-chains-entry-point.sh /wd/5-chains-entry-point.sh
COPY docker/5-chains-daemons.proc /wd/5-chains-daemons.proc
COPY docker/regtest-entry-point.sh /wd/regtest-entry-point.sh
COPY docker/regtest-daemons.proc /wd/regtest-daemons.proc
COPY docker/2-chains-entry-point.sh /wd/2-chains-entry-point.sh
COPY docker/2-chains-daemons.proc /wd/2-chains-daemons.proc
CMD bash 2-chains-entry-point.sh
