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

# This is only needed for elements-cli for lightning
ENV SHA256SUM_ELEMENTS=8119ec068f3b143a745d4731a9221b9e6d0df2340a357147c9c9f68db74204a1
RUN curl -sL -o elements.tar.gz https://github.com/ElementsProject/elements/releases/download/elements-0.17.0.3/elements-0.17.0.3-x86_64-linux-gnu.tar.gz \
 && echo "${SHA256SUM_ELEMENTS}  elements.tar.gz" | sha256sum --check \
 && tar xzf elements.tar.gz \
 && rm /wd/elements-0.17.0/README.md \
 && rm /wd/elements-0.17.0/bin/elements-qt \
 && rm /wd/elements-0.17.0/bin/elements-tx \
 && rm /wd/elements-0.17.0/bin/elementsd \
 && rm /wd/elements-0.17.0/bin/test_bitcoin \
 && rm /wd/elements-0.17.0/include/bitcoinconsensus.h \
 && rm /wd/elements-0.17.0/lib/libelementsconsensus.so \
 && rm /wd/elements-0.17.0/lib/libelementsconsensus.so.0 \
 && rm /wd/elements-0.17.0/lib/libelementsconsensus.so.0.0.0 \
 && rm /wd/elements-0.17.0/share/man/man1/bitcoin-qt.1 \
 && rm /wd/elements-0.17.0/share/man/man1/elements-cli.1 \
 && rm /wd/elements-0.17.0/share/man/man1/elements-tx.1 \
 && rm /wd/elements-0.17.0/share/man/man1/elementsd.1 \
 && rm elements.tar.gz
ENV PATH="/wd/elements-0.17.0/bin:${PATH}"

COPY docker/build-clightning.sh /wd/build-clightning.sh
ENV LN_BRANCH_COMMIT=v0.8.0-demo-10
ENV LN_REPO_HOST=https://github.com/jtimon
ENV LN_REPO_NAME=lightning
RUN bash build-clightning.sh $LN_BRANCH_COMMIT $LN_REPO_NAME $LN_REPO_HOST
ENV PATH="/wd/$LN_REPO_NAME/lightningd:${PATH}"

COPY conf /wd/conf
