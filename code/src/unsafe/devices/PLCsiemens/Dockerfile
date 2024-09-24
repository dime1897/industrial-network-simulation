FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update \
    && apt install -y software-properties-common \
                        python3-pip \
    && add-apt-repository ppa:gijzelaar/snap7 \
    && apt install -y libsnap7-dev libsnap7-1 \
    && apt-get install -y \
    net-tools \
    iputils-ping \
    tcpdump \
    iptables \
    iproute2 \
    dnsutils \
    netcat-traditional \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && mkdir /app

WORKDIR /app

COPY . .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt
