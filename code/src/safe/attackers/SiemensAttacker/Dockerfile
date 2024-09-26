FROM python:latest
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update \
    && apt-get install -y \
    net-tools \
    iputils-ping \
    tcpdump \
    iptables \
    iproute2 \
    dnsutils \
    netcat-traditional \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

COPY . .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt