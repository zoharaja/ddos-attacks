from scapy.all import sniff, IP, TCP
import mysql.connector
from datetime import datetime
import threading
import subprocess

# Tracking
syn_counts = {}
alert_threshold = 2  # lower for testing
window_seconds = 5
lock = threading.Lock()

def reset_counts():
    global syn_counts
    with lock:
        syn_counts = {}
    threading.Timer(window_seconds, reset_counts).start()

reset_counts()

def log_to_mysql(src_ip, dst_ip):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="claire",
            password="testpass",
            database="ids_logs"
        )
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO syn_alerts (timestamp, source_ip, dest_ip, protocol, alert)
            VALUES (%s, %s, %s, %s, %s)
        """, (datetime.now(), src_ip, dst_ip, "TCP", "SYN flood threshold exceeded and blocked"))
        db.commit()
        cursor.close()
        db.close()
        print(f"[!] ALERT: SYN flood from {src_ip} -> {dst_ip} (logged)")
    except Exception as e:
        print("Logging error:", e)

def block_ip(ip):
    print(f"[DEBUG] Trying to block IP: {ip}")
    try:
        result = subprocess.run(
            ["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
            check=True,
            stderr=subprocess.PIPE
        )
        print(f"[+] BLOCKED IP: {ip}")
    except subprocess.CalledProcessError as e:
        print(f"[X] Failed to block {ip}: {e}")

def detect_syn(pkt):
    if pkt.haslayer(TCP) and pkt[TCP].flags & 0x02:
        if pkt.haslayer(IP):
            src_ip = pkt[IP].src
            dst_ip = pkt[IP].dst
            print(f"[*] SYN from {src_ip} to {dst_ip}")
            with lock:
                syn_counts[src_ip] = syn_counts.get(src_ip, 0) + 1
                print(f"[*] Count for {src_ip}: {syn_counts[src_ip]}")
                if syn_counts[src_ip] >= alert_threshold:
                    print(f"[!!] THRESHOLD EXCEEDED for {src_ip}")
                    log_to_mysql(src_ip, dst_ip)
                    block_ip(src_ip)



# Demo mode: inject fake SYN packets to test system
from scapy.all import send, Ether

def inject_test_syn():
    print("[DEMO] ")
    for i in range(3):
        pkt = IP(src="192.168.10.88", dst="10.0.2.15") / TCP(sport=12345+i, dport=80, flags="S")
        send(pkt, iface="enp0s3", verbose=False)

# Delay to let sniffer start first
threading.Timer(2.0, inject_test_syn).start()

print("IPS is running")
print("Sniffing on enp03")
sniff(filter="tcp", prn=detect_syn, iface="enp0s3", store=0)


