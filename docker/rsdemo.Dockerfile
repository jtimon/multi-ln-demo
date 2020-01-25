FROM ubuntu:18.04

RUN apt-get -yqq update \
  && apt-get install -qfy \
    build-essential \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /wd

# Install cargo for rust builds
RUN cd /root \
    && curl -s -L -O https://static.rust-lang.org/rustup.sh \
    && bash ./rustup.sh -y --verbose
ENV PATH="/root/.cargo/bin:${PATH}"

COPY rustdemo/Cargo.toml /wd/rustdemo/Cargo.toml
COPY rustdemo/src /wd/rustdemo/src
RUN cd /wd/rustdemo && \
    cargo test && \
    cargo build --release
