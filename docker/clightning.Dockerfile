FROM ubuntu:18.04

RUN apt-get -yqq update \
  && apt-get install -qfy \
    curl \
    libsodium-dev \
    xz-utils \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

# TODO remove everything except /wd/bitcoin-0.19.0.1/bin/bitcoin-cli
# This is only needed for bitcoin-cli for lightning
ENV SHA256SUM_BITCOINCORE=732cc96ae2e5e25603edf76b8c8af976fe518dd925f7e674710c6c8ee5189204
RUN curl -sL -o bitcoin.tar.gz https://bitcoincore.org/bin/bitcoin-core-0.19.0.1/bitcoin-0.19.0.1-x86_64-linux-gnu.tar.gz \
 && echo "${SHA256SUM_BITCOINCORE}  bitcoin.tar.gz" | sha256sum --check \
 && tar xzf bitcoin.tar.gz -C /wd \
 && rm bitcoin.tar.gz
ENV PATH="/wd/bitcoin-0.19.0.1/bin:${PATH}"

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

ENV SHA256SUM_CLIGHTNING=0da11624b178277f6e498b241df78e94d1da6e115954d91eb22f92e462d2b7bf
RUN curl -sL -o lighting.tar.xz https://github.com/ElementsProject/lightning/releases/download/v0.8.0/clightning-v0.8.0-Ubuntu-18.04.tar.xz \
 && echo "${SHA256SUM_CLIGHTNING}  lighting.tar.xz" | sha256sum --check \
 && ls \
 && tar xf lighting.tar.xz -C /wd \
 && rm /wd/usr/bin/lightning-cli \
 && rm -r /wd/usr/share \
 && rm lighting.tar.xz
ENV PATH="/wd/usr/bin:${PATH}"

COPY conf /wd/conf
