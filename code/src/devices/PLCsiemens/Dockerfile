FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update \
    && apt install -y software-properties-common \
                        python3-pip \
                        python3-venv \
    && add-apt-repository ppa:gijzelaar/snap7 \
    && apt install -y libsnap7-dev libsnap7-1 \
    && apt update 

RUN mkdir /app
WORKDIR /app

COPY . .
RUN pip3 install --break-system-packages --no-cache-dir -r requirements.txt

CMD ["python3", "PLCsiemens.py"]
