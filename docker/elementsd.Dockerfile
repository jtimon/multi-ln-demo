FROM ubuntu:18.04

RUN apt-get -yqq update \
  && apt-get install -qfy \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

# TODO remove everything except /wd/elements-0.17.0/bin/elementsd
ENV SHA256SUM_ELEMENTS=8119ec068f3b143a745d4731a9221b9e6d0df2340a357147c9c9f68db74204a1
RUN curl -sL -o elements.tar.gz https://github.com/ElementsProject/elements/releases/download/elements-0.17.0.3/elements-0.17.0.3-x86_64-linux-gnu.tar.gz \
 && echo "${SHA256SUM_ELEMENTS}  elements.tar.gz" | sha256sum --check \
 && tar xzf elements.tar.gz \
 && rm elements.tar.gz
ENV PATH="/wd/elements-0.17.0/bin:${PATH}"

COPY conf/bitcoind.conf /wd/conf/bitcoind.conf
