
from scapy.all import sniff, IP, TCP, conf
import mysql.connector
from datetime import datetime, timedelta
import threading

# Track SYN packet counts
syn_counts = {}
THRESHOLD = 5  # packets
WINDOW = 5  # seconds

def reset_counts():
    global syn_counts
    syn_counts = {}
    threading.Timer(WINDOW, reset_counts).start()

reset_counts()  # start reset loop

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
        """, (datetime.now(), src_ip, dst_ip, "TCP", "SYN flood threshold exceeded"))
        db.commit()
        cursor.close()
        db.close()
        print(f"[!] ALERT: SYN flood from {src_ip} to {dst_ip} (logged)")
    except Exception as e:
        print("Logging error:", e)

def detect_syn(pkt):
    if pkt.haslayer(TCP) and pkt[TCP].flags & 0x02:
        if IP in pkt:
            src = pkt[IP].src
            dst = pkt[IP].dst
            syn_counts[src] = syn_counts.get(src, 0) + 1

            if syn_counts[src] == THRESHOLD:
                log_to_mysql(src, dst)

print("IDS IS RUNNING")
print("\nAvailable interfaces:", conf.ifaces)
sniff(filter="tcp", prn=detect_syn, iface="enp0s3", store=0)
