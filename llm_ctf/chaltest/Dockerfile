FROM ctfenv

USER root

# Updating apt to see and install Google Chrome
RUN apt-get -y update && apt-get install -y wget

# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'


# Magic happens
RUN apt-get -y update && apt-get install -y google-chrome-stable

# Installing Unzip
RUN apt-get install -yqq unzip jq

RUN google-chrome --version | grep -Eo '\b[0-9.]+\b' | cut -d. -f1-3 > /tmp/chrome_version
RUN echo "browser version: $(cat /tmp/chrome_version)"
RUN curl -s https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build-with-downloads.json | \
    jq -r '.builds."'$(cat /tmp/chrome_version)'".downloads.chromedriver[] | select(.platform == "linux64") | .url' \
    | xargs wget -q -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip chromedriver-linux64/chromedriver && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rmdir chromedriver-linux64 && \
    echo "chromedriver version:" && \
    chromedriver --version && \
    google-chrome --version

RUN apt-get install -y p11-kit p11-kit-modules
RUN ln -s -f /usr/lib/x86_64-linux-gnu/pkcs11/p11-kit-trust.so /usr/lib/x86_64-linux-gnu/nss/libnssckbi.so
ADD llmctf.crt /usr/local/share/ca-certificates/llmctf.crt
RUN chmod 644 /usr/local/share/ca-certificates/llmctf.crt && update-ca-certificates

USER ctfplayer

# Set display port as an environment variable
ENV DISPLAY=:99
ENV TERM=xterm-256color

RUN pip install selenium

COPY webtester.py /home/ctfplayer/webtester.py

CMD ["/bin/bash"]
