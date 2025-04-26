# Zoha Raja         CSCE 3560.001       Group 4

# Dockerfile

# create image from python 3.10
FROM python:3.10-slim

# print logs immediately without delays
ENV PYTHONUNBUFFERED=1

# install necessary dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      iptables \
      libcap2-bin \
      libpcap-dev \
      iputils-ping \
      procps \
      sqlite3 \
 && rm -rf /var/lib/apt/lists/*

# install necessary packages
RUN pip install --no-cache-dir scapy

# copy idps.py to container + make it executable
COPY idps.py /usr/local/bin/idps.py
RUN chmod +x /usr/local/bin/idps.py

# let python sniff packets and change firewall rules without root user privileges
RUN setcap cap_net_raw,cap_net_admin+eip $(readlink -f $(which python3))

# create new folder for database
VOLUME /data

# execute idps.py
ENTRYPOINT ["python3", "-u", "/usr/local/bin/idps.py"]
