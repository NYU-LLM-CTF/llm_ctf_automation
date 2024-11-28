FROM ubuntu:22.04
# Force platform to x86_64
ARG TARGETPLATFORM
ENV DEBIAN_FRONTEND=noninteractive
RUN dpkg --add-architecture i386
RUN apt-get update && apt-get install -y \
    sudo curl netcat \
    build-essential pkg-config gdb gdbserver \
    python3-dev python3-pip python3-venv \
    libssl-dev libffi-dev \
    libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev \
    bsdmainutils file \
    sagemath sqlmap nikto apktool \
    libc6-i386 libc6-dev:i386 gcc-multilib \
    g++-multilib \
    wget jq vim \
    p11-kit p11-kit-modules \
    rustc cargo sleuthkit \
    openjdk-17-jdk openjdk-17-jre \
    && rm -rf /var/lib/apt/lists/*

ARG HOST_UID=1000

# Create a non-root user with sudo permissions
ARG USERNAME=ctfplayer
ARG USER_UID=$HOST_UID
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Install radare2
WORKDIR /tmp
RUN curl -LO https://github.com/radareorg/radare2/releases/download/5.8.8/radare2_5.8.8_amd64.deb && \
    curl -LO https://github.com/radareorg/radare2/releases/download/5.8.8/radare2-dev_5.8.8_amd64.deb && \
    apt-get install -y ./radare2_5.8.8_amd64.deb ./radare2-dev_5.8.8_amd64.deb && \
    rm -f ./radare2-dev_5.8.8_amd64.deb ./radare2_5.8.8_amd64.deb

# Install Ghidra
RUN wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.0.1_build/ghidra_11.0.1_PUBLIC_20240130.zip && \
    unzip -d /opt/ghidra ghidra_11.0.1_PUBLIC_20240130.zip && \
    rm ghidra_11.0.1_PUBLIC_20240130.zip
RUN mkdir /opt/ghidra/customScripts/
COPY ghidra_scripts/DecompileToJson.java  /opt/ghidra/customScripts/DecompileToJson.java
COPY ghidra_scripts/DisassembleToJson.java  /opt/ghidra/customScripts/DisassembleToJson.java
COPY ghidra_scripts/decompile.sh  /opt/ghidra/customScripts/decompile.sh
COPY ghidra_scripts/disassemble.sh  /opt/ghidra/customScripts/disassemble.sh

# Install apktool and jadx
RUN curl -LO https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip && \
    unzip -d /usr/local jadx-1.4.7.zip && \
    rm -f jadx-1.4.7.zip
    

# Force Chrome to use the system CA store
RUN ln -s -f /usr/lib/x86_64-linux-gnu/pkcs11/p11-kit-trust.so /usr/lib/x86_64-linux-gnu/nss/libnssckbi.so
RUN ln -s -f /usr/lib/x86_64-linux-gnu/pkcs11/p11-kit-trust.so /usr/lib/firefox/libnssckbi.so || true

# Switch to user
USER $USERNAME
WORKDIR /home/$USERNAME

# Install pwntools
ENV VIRTUAL_ENV=/home/$USERNAME/.ctfenv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -U pip && pip install pwntools gmpy2 angr chepy

RUN mkdir ctf_files

# Copy in the entrypoint script
COPY entrypoint.sh /home/$USERNAME/.entrypoint.sh
CMD ["bash", "/home/ctfplayer/.entrypoint.sh"]
