FROM ubuntu:18.04

RUN apt-get -yqq update \
  && apt-get install -qfy \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

ENV SHA256SUM_ELEMENTS=8119ec068f3b143a745d4731a9221b9e6d0df2340a357147c9c9f68db74204a1
RUN curl -sL -o elements.tar.gz https://github.com/ElementsProject/elements/releases/download/elements-0.17.0.3/elements-0.17.0.3-x86_64-linux-gnu.tar.gz \
 && echo "${SHA256SUM_ELEMENTS}  elements.tar.gz" | sha256sum --check \
 && tar xzf elements.tar.gz \
 && rm /wd/elements-0.17.0/README.md \
 && rm /wd/elements-0.17.0/bin/elements-cli \
 && rm /wd/elements-0.17.0/bin/elements-qt \
 && rm /wd/elements-0.17.0/bin/elements-tx \
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

COPY conf/bitcoind.conf /wd/conf/bitcoind.conf
