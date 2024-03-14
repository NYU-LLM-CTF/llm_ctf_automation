FROM ubuntu:22.04
# Force platform to x86_64
ARG TARGETPLATFORM
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    vim \
    cmake \
    git \
    libgtk2.0-dev \
    pkg-config \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    python3-dev \
    python3-numpy \
    python3-pip \
    libssl-dev \
    libffi-dev \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    ubuntu-desktop \
    bc \
    bsdmainutils \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user with sudo permissions
ARG USERNAME=ctfplayer
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install radare2
WORKDIR /tmp
RUN apt-get install -y curl netcat python3-venv qemu-user qemu-user-static
RUN wget https://github.com/radareorg/radare2/releases/download/5.8.8/radare2-dev_5.8.8_amd64.deb \
         https://github.com/radareorg/radare2/releases/download/5.8.8/radare2_5.8.8_amd64.deb && \
        apt-get install -y ./radare2-dev_5.8.8_amd64.deb ./radare2_5.8.8_amd64.deb && \
        rm -rf ./radare2-dev_5.8.8_amd64.deb ./radare2_5.8.8_amd64.deb

# Sagemath
RUN apt-get install -y sagemath

# sqlmap and nikto
RUN apt-get install -y sqlmap nikto

# Install apktool and jadx
RUN apt-get install -y apktool
RUN wget https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip
RUN unzip -d /usr/local jadx-1.4.7.zip
RUN rm -f jadx-1.4.7.zip

# Switch to user
USER $USERNAME
WORKDIR /home/$USERNAME

# Install pwntools
ENV VIRTUAL_ENV=/home/$USERNAME/.ctfenv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -U pip
RUN pip install pwntools ipython gmpy2

# Copy in the entrypoint script
COPY entrypoint.sh /home/$USERNAME/.entrypoint.sh
CMD ["bash", "/home/ctfplayer/.entrypoint.sh"]
