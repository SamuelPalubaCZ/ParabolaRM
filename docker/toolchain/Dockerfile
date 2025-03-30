# Dockerfile for Parabola RM Builder Toolchain
# This Dockerfile creates a container with the cross-compilation toolchain for the reMarkable tablet

FROM debian:bullseye

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        git \
        make \
        cmake \
        python3 \
        python3-pip \
        wget \
        xz-utils \
        bison \
        flex \
        libssl-dev \
        bc \
        device-tree-compiler \
        u-boot-tools \
        libncurses-dev \
        ccache \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download and install the reMarkable toolchain
RUN mkdir -p /opt/toolchain && \
    cd /opt/toolchain && \
    wget -q https://ipfs.eeems.website/ipfs/Qmdkdeh3bodwDLM9YvPrMoAi6dFYDDCodAnHvjG5voZxiC -O toolchain.tar.gz && \
    tar xf toolchain.tar.gz && \
    rm toolchain.tar.gz

# Set up environment variables for the toolchain
ENV PATH="/opt/toolchain/poky-2.1.3/sysroots/x86_64-pokysdk-linux/usr/bin:/opt/toolchain/poky-2.1.3/sysroots/x86_64-pokysdk-linux/usr/sbin:${PATH}"
ENV OECORE_NATIVE_SYSROOT="/opt/toolchain/poky-2.1.3/sysroots/x86_64-pokysdk-linux"

# Create a working directory
WORKDIR /workspaces

# Set the entrypoint
ENTRYPOINT ["/bin/bash"]