# Zoha Raja     CSCE 3560.001       Group 4

#!/usr/bin/env python3

# libraries
import time
import threading
import subprocess
import sqlite3
import sys
from collections import deque
from scapy.all import sniff, ICMP

# database path
DB_PATH = '/data/icmp_logs.db'
BASE_THRESHOLD = 20      # packet threshold
WINDOW_DURATION = 10     # time interval/threshold

# timestamps for packets + signal to end monitoring
icmp_timestamps = deque()
attack_mitigated = False

# initialize SQLite database
def init_database():

    # connect to database
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        # create table in database
        c.execute("""
            CREATE TABLE IF NOT EXISTS icmp_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
        """)

        # save database changes
        conn.commit()

# add each event to database
def record_event(event_type, timestamp):

    # connect to database
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        # enter type od event with time in table
        c.execute(
            "INSERT INTO icmp_events (event_type, timestamp) VALUES (?, ?)",
            (event_type, timestamp)
        )

        # save database changes
        conn.commit()

# record each packet and its timestamp
def handle_icmp(pkt):

    # see if packet is an ICMP echo packet
    if pkt.haslayer(ICMP):

        # retrieve + save packet timestamp
        timestamp = time.time()
        icmp_timestamps.append(timestamp)

        # print each packet with timestamp
        print(f"[+] ICMP packet logged at {timestamp}")

        # store packet log in database
        record_event("RECEIVED", timestamp)

# count and monitor each packet
def monitor_traffic():
    global attack_mitigated

    # monitor packets until attack is mitigated
    while not attack_mitigated:

        # log current time
        now = time.time()

        # remove old packets before this session
        while icmp_timestamps and icmp_timestamps[0] < now - WINDOW_DURATION:
            icmp_timestamps.popleft()

        # number of new packets
        packet_count = len(icmp_timestamps)

        # calculate rate of packets
        packet_rate = packet_count / WINDOW_DURATION

        threshold = BASE_THRESHOLD

        # lower threshold if packet count is too high
        if packet_count > BASE_THRESHOLD * 2:
            print("High volume of packets. Temporarily decreasing threshold.")
            threshold = BASE_THRESHOLD // 2

        # once threshold is exceeded, execute mitigation
        if packet_count > threshold:
            print(f"Threshold exceeded: {packet_count} packets in {WINDOW_DURATION}s (Rate: {packet_rate:.2f} pps)")
            apply_mitigation()

        # sleep for 1 second before checking again
        time.sleep(1)

# automatically block packets after reaching threshold
def apply_mitigation():
    global attack_mitigated

    # get time
    timestamp = time.time()

    # iptables rule to drop packets
    print("Applying firewall rules to drop ICMP packets...")
    subprocess.run([
        "iptables", "-A", "INPUT",
        "-p", "icmp", "--icmp-type", "echo-request",
        "-j", "DROP"
    ], check=True)
    print("Firewall rules applied.")

    # kill ping process
    print("Terminating active ping processes...")
    subprocess.run(["pkill", "-9", "ping"], check=False)

    # record mitigation in database
    record_event("MITIGATED", timestamp)

    # signal that attack was mitigated
    attack_mitigated = True

    # shut down threads before exiting
    print("Mitigation is done. Shutting down packet sniffer...")
    time.sleep(2)

# main function
def main():
    # create database
    init_database()

    # create and start thread to monitor packet rate in background
    monitor_thread = threading.Thread(target=monitor_traffic, daemon=True)
    monitor_thread.start()

    print("Sniffing ICMP packets...")

    # begin sniffing packets
    sniff(
        iface="lo", # loopback interface
        filter="icmp",  # icmp packets
        prn=handle_icmp,
        store=0,
        stop_filter=lambda pkt: attack_mitigated    # stop sniffing packets
    )

# execute program
if __name__ == "__main__":
    main()
