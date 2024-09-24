FROM python:latest
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y \
    && apt-get install -y \
    net-tools \
    iputils-ping \
    tcpdump \
    iptables \
    iproute2 \
    dnsutils \
    netcat-traditional \
    && mkdir /app

WORKDIR /app

COPY . .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt
