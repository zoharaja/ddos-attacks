#!/usr/bin/python3

import os
import time
import signal
import sqlite3
from datetime import datetime
from threading import Thread
from flask import Flask, render_template_string, request
import tkinter as tk
from tkinter import messagebox


# Flask is a Python Web Development Framework used in by the IDPS for hosting and displaying monitoring information
# Initializing Flask
app = Flask(__name__)


THRESHOLD_KB = 100_0000 # Threshold Limit in KB for System Memory(10000 MB) 
WHITELISTING_PROC = {"sshd", "init", "systemd", "oom_killer"} # Whitelist important system processes to avoid unstable state
SQLITE_PATH = 'oom_log.db' #  Local Sqlite DB path



# This HTML code is used by IDPS to host and show the killed processes with relevant information.
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>IDPS Monitoring Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(120deg, #f6f8fa, #dbe9f4);
            margin: 0;
            padding: 40px;
            color: #333;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
        }
        form {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
            background: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        input, select, button {
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 16px;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #2980b9;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: #fff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
        }
        th, td {
            padding: 15px;
            border-bottom: 1px solid #eee;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .container {
            max-width: 1200px;
            margin: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>IDPS Activity Dashboard</h1>

        <table>
            <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>PID</th>
                <th>Process Name</th>
                <th>Process Memory (MB)</th>
                <th>Available Memory (MB)</th>
            </tr>
            {% for row in logs %}
            <tr>
                <td>{{ row[0] }}</td>
                <td>{{ row[1] }}</td>
                <td>{{ row[2] }}</td>
                <td>{{ row[3] }}</td>
                <td>{{ row[4] }}</td>
                <td>{{ row[5] }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

#This function creates a local database if does ont exist on the SQLITE_PATH
def setup_database():
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oom_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pid INTEGER,
            name TEXT,
            rss_kb INTEGER,
            available_kb INTEGER
        )
    ''')
    conn.commit()
    conn.close()

#This fucntion stores the killed process information in the local SQLite database
def log_to_database(pid, name, rss_kb,avail):
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO oom_log (timestamp, pid, name, rss_kb,available_kb)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), pid, name, rss_kb/1000,avail/1000))
    conn.commit()
    conn.close()

# This fucntion uses the /proc/meminfo to get system memory information
def get_available_memory_kb():
    with open("/proc/meminfo", "r") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    return -1

# This fucntion uses /proc and /proc/pid/status to get relevant processes information
def get_processes_memory_usage():
    processes = []
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                with open(f"/proc/{pid}/status") as f:
                    name = ""
                    rss = 0
                    for line in f:
                        if line.startswith("Name:"):
                            name = line.split()[1].strip()
                        elif line.startswith("VmRSS:"):
                            rss = int(line.split()[1])
                    if name and rss > 0 and name not in WHITELISTING_PROC:
                        processes.append((int(pid), name, rss))
            except Exception:
                continue
    return processes

# This function is called when a process utilizes too much memory and has to be killed to avoid deadloacks and unstable state
def kill_process(pid, name, rss , ava):
    root = tk.Tk()
    root.withdraw()
    try:
        
        log_to_database(pid, name, rss, ava)
        os.kill(pid, signal.SIGKILL)
        print(f"The following Process Name and ID has been terminated:\nProcess Name: {name}\nProcess ID: {pid}\nProcess Memory: {rss/1000} MB")
        messagebox.showinfo("Information",f"Successfully stopped the process with the follwong details:\nProcess Name: {name}\nProcess ID: {pid}")
    except Exception as e:
        print(f"Failed to kill the following Process Name and ID:\nProcess Name: {name}\nProcess ID: {pid}\Failure Reason: {e}")
        messagebox.showinfo("Information",f"Failed to kill the process with the following details:\nProcess Name: {name}\nProcess ID: {pid}")
    root.destroy()

# This is a main continous function that detects and prevents Host-Based Attacks and handles the IDPS operations 
def oom_killer_loop():
    setup_database()
    print(f"Custom IDPS program started (threshold: {THRESHOLD_KB} KB)\n")
    while True:
        available = get_available_memory_kb()
        if available > 0 and available < THRESHOLD_KB:
            processes = get_processes_memory_usage()
            if processes:
                pid, name, rss = max(processes, key=lambda x: x[2])
                print(f"[!] Low memory. Attempting to kill PID {pid} ({name}) using {rss} KB")
                kill_process(pid, name, rss, available)
        time.sleep(2)

# This function intializes the monitoring dashboard for the IDPS using Flask
@app.route('/')
def dashboard():
    process_filter = request.args.get('process', '').strip()
    min_rss = request.args.get('min_rss', '').strip()
    max_rss = request.args.get('max_rss', '').strip()

    query = "SELECT * FROM oom_log WHERE 1=1"
    params = []

    # if process_filter:
    #     query += " AND name LIKE ?"
    #     params.append(f"%{process_filter}%")

    # if min_rss.isdigit():
    #     query += " AND rss_kb >= ?"
    #     params.append(int(min_rss))

    # if max_rss.isdigit():
    #     query += " AND rss_kb <= ?"
    #     params.append(int(max_rss))

    query += " ORDER BY timestamp DESC"

    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()

    return render_template_string(TEMPLATE, logs=logs, request=request)

# Main fucntion of the program
if __name__ == '__main__':
    Thread(target=oom_killer_loop, daemon=True).start()
    app.run(debug=True, port=5000)
