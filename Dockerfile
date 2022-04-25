FROM ubuntu:20.04

RUN apt-get update && \
    DEBIAN_FRONTEND='noninteractive' \
    apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3-pip \
    wget \
    curl \
    firefox

# Install the latest version of Geckodriver:
RUN BASE_URL=https://github.com/mozilla/geckodriver/releases/download \
    && VERSION=$(curl -sL \
    https://api.github.com/repos/mozilla/geckodriver/releases/latest | \
    grep tag_name | cut -d '"' -f 4) \
    && curl -sL "$BASE_URL/$VERSION/geckodriver-$VERSION-linux64.tar.gz" | \
    tar -xz -C /usr/local/bin

COPY . /opt/gmg/

RUN cd /opt/gmg && \
    python3.9 -m pip install -r requirements.txt && \
    python3.9 setup.py install 

CMD ["gmg"]
