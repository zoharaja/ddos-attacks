# Use the latest Ubuntu image
FROM ubuntu:latest

# Set environment variable to avoid interaction
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install Python and required libraries
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-psutil \
    nano \
    curl

# Copy the forkbomb and monitor script into the container
COPY forkbomb.sh /usr/local/bin/forkbomb.sh
COPY monitor.py /usr/local/bin/monitor.py

# Make forkbomb script executable
RUN chmod +x /usr/local/bin/forkbomb.sh

# Set default command to run
CMD ["/bin/bash"]
