# DDOS-Attacks


**Host IDPS to Detect and Prevent Resource Exhaustion Attacks (Syed Danish Hussaini)**

The main aim of this project is to detect, prevent and monitor resource exhaustion attacks using custom Python-based Host IDPS (Intrusion Detection and Prevention System). The IDPS detects high usage process and triggers the prevention mechanism by terminating the process. The operations by the IDPS are logged in a local SQLite database. The logs from these local DB are then hosted on a small Flask web application that displays relevant infomation about the IDPS operations.

This project contains the follwing files:
- `idps.py`: This Python file contains code that controls the IDPS operations and also hosts the Flask web-application
- `resExhaus.py`: This Python file contains the resource exhaustion attack code.
- `resExhaus`: This is same as `resExhaus.py`, but compiled as an executable.
- `requirements.txt`: This file contains the Python libraires required to execute the IDPS.

**Execution Steps**

1. We first execute the custom IDPS that starts the detecton mechansism and monitors the system memory every second. To execute the custom IDPS, we need to run the Python file as follows:
   
        sudo python3 idps.py

2. After we run the idps.py file, we can see the IDPS web application hosted on port 5000 on the local Flask server. You can open a browser on the machine and paste the following URL to see the IDPS monitoring Dashboard:
   
        http://localhost:5000  

3. Now that we have IDPS running, we can either execute the Python resExhaus.py attack file or the resExhaus executable. The execution of these files will perform a Resource Exhaustino Attack on the local machine causing it to allocate more resources than it has. Run the following commands to execute the attack:
   
        python3 resExhaus.py

   OR

        ./resExhaus

4.  Now that we have executed the attack, the IDPS detects and prevents the attack file by terminating the malicious process and displays a informative TextBox displaying the process ID and name of the malicious process terminated. These operations by IDPS also logged in the local database `oom_killer.db` and reflected on the Flask web-applcation hosting the IDPS monitoring dashboard. 

---

**Fork Bomb Attack Detection and Prevention (Hafsah Iqbal)**

For the demonstration of the **Fork Bomb Attack**, I will show how the system detects and mitigates the attack within a Docker container. The IDPS (Intrusion Detection and Prevention System) monitors the number of processes running on the system and can automatically terminate malicious processes if an abnormal number is detected, preventing a system crash caused by the fork bomb.

**Files**
- `monitor.py`: Python script that detects and mitigates the fork bomb attack.
- `forkbomb.sh`: Bash script to create a fork bomb by continuously forking new processes.

**Requirements:**
- Docker application
- Python 3.x
- psutil library for Python (installed using `pip install psutil`)

**Execution Instructions**
1. Start by building the Docker container and running it:
    ```bash
    docker build -t forkbomb-container .
    docker run -it forkbomb-container
    ```

2. Inside the container, open and execute the Fork Bomb script:
    a) Open the `forkbomb.sh` script in nano or vi:
    ```bash
    nano /usr/local/bin/forkbomb.sh
    ```

    b) Make the script executable:
    ```bash
    chmod +x /usr/local/bin/forkbomb.sh
    ```

    c) Run the Fork Bomb script:
    ```bash
    /usr/local/bin/forkbomb.sh
    ```

3. On the host machine, start the monitoring system:
    ```bash
    python3 monitor.py
    ```

4. Show the logs for the attack:
    ```bash
    cat attack_log.txt
    ```
    *********************************************************************************************************************************************************************************************
   
**Network-Based Attack for Container (Zoha Raja): ICMP Ping Flood Attack**

For the network-based attack for a container, I chose to demonstrate the execution and mitigation of an ICMP flood attack. An IDPS is launched inside of a Docker container, and it monitors ping traffic on the loopback (lo) interface. The IDPS detects ICMP flood attacks and automatically mitigates them by dropping incoming ICMP echo-requests and terminating the active processes. The incoming packets and their mitigation are logged into a SQLite database.

**Files**
-	idps.py: Python script to mitigate ICMP flood attacks
-	Dockerfile: Used to build a docker container with necessary dependencies
  
**Requirements:**
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
3.	Open two terminal windows.
4.	In terminal 1, navigate to the directory containing idps.py and Dockerfile
6.	Also, in terminal 1, build the container by entering the following command:
   
         docker build -t icmp-idps .

8.	Finally, in terminal 1, start the IDPS by entering the following command:
   
         docker run --rm -v "$(pwd)/data:/data" --cap-add=NET_ADMIN --cap-add=NET_RAW icmp-idps
  	
10.	In terminal 2, start the ICMP flood attack by entering the following command:
    
         docker exec -it icmp-flood sh -c "ping -f 127.0.0.1"

12.	To view the events logged in the database, execute the following command in terminal 2:
    
          sqlite3 ./data/icmp_logs.db "SELECT * FROM icmp_events;"
   	
*********************************************************************************************************************************************************************************************

