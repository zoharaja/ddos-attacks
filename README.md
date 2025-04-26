# ddos-attacks

**Network-Based Attack for Container (Zoha Raja): ICMP Ping Flood Attack**
For the network-based attack for a container, I chose to demonstrate the execution and mitigation of an ICMP flood attack. An IDPS is launched inside of a Docker container, and it monitors ping traffic on the loopback (lo) interface. The IDPS detects ICMP flood attacks and automatically mitigates them by dropping incoming ICMP echo-requests and terminating the active processes. The incoming packets and their mitigation are logged into a SQLite database.

**Files**
-	idps.py: Python script to mitigate ICMP flood attacks
-	Dockerfile: Used to build a docker container with necessary dependencies
Requirements:
-	Docker application
The following dependencies will be installed automatically upon building the Docker container:
-	Python 3.10
-	Scapy
-	iptables
-	sqlite3
-	iputils-ping
-	libcap2-bin
-	libcap-dev

**Execution instructions**
1.	Download idps.py and Dockerfile
2.	Ensure that Docker is installed and active
3.	Navigate to the directory containing idps.py and Dockerfile
4.	Open two terminal windows
5.	In terminal 1, build the container by entering the following command:
         docker build -t icmp – idps .

7.	Also in terminal 1, start the IDPS by entering the following command:
         docker run –rm -v "$(pwd)/data:/data" –cap-add=NET_ADMIN –cap-add=NET_RAW icmp-idps

8.	In terminal 2, start the ICMP flood attack by entering the following command:
         docker exec -it icmp-flood sh -c "ping -f 127.0.0.1"

10.	To view the events logged in the database, execute the following command in terminal 2:
          sqlite3. /data/icmp_logs.db "SELECT * FROM icmp_events;"
   	
*************************************************************************************************************************************************


