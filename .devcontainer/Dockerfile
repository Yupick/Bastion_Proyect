FROM mcr.microsoft.com/devcontainers/python:3.12

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    build-essential cmake ninja-build libssl-dev pkg-config libffi-dev git curl wget openjdk-11-jdk \
  && rm -rf /var/lib/apt/lists/*

# Install rustup (non-interactive)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y \
  && /root/.cargo/bin/rustup default stable

# Install Node (via NodeSource)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y nodejs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
