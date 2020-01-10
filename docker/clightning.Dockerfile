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

# TODO remove everything except /wd/elements-0.17.0.3/bin/elements-cli
# This is only needed for elements-cli for lightning
ENV SHA256SUM_ELEMENTS=8119ec068f3b143a745d4731a9221b9e6d0df2340a357147c9c9f68db74204a1
RUN curl -sL -o elements.tar.gz https://github.com/ElementsProject/elements/releases/download/elements-0.17.0.3/elements-0.17.0.3-x86_64-linux-gnu.tar.gz \
 && echo "${SHA256SUM_ELEMENTS}  elements.tar.gz" | sha256sum --check \
 && tar xzf elements.tar.gz \
 && rm elements.tar.gz
ENV PATH="/wd/elements-0.17.0/bin:${PATH}"

ENV SHA256SUM_CLIGHTNING=e36d259696ad172d509be712c0ee96b64a454d9a836b7a576d0bc26a580b313e
RUN curl -sL -o lighting.tar.xz https://github.com/ElementsProject/lightning/releases/download/v0.7.3/clightning-v0.7.3-Ubuntu-18.04.tar.xz \
 && echo "${SHA256SUM_CLIGHTNING}  lighting.tar.xz" | sha256sum --check \
 && ls \
 && tar xf lighting.tar.xz -C /wd \
 && rm /wd/usr/bin/lightning-cli \
 && rm -r /wd/usr/share \
 && rm lighting.tar.xz
ENV PATH="/wd/usr/bin:${PATH}"

COPY conf /wd/conf
