import psutil
import time
import os

# Define threshold values for detecting attacks (you can adjust these values as needed)
CPU_THRESHOLD = 90  # Percent usage to consider as high CPU
PROCESS_THRESHOLD = 1000  # Process count to consider as abnormal (adjust based on your system)

# Function to check CPU usage
def check_cpu_usage():
    cpu_usage = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_usage}%")
    return cpu_usage

# Function to check memory usage
def check_memory_usage():
    memory = psutil.virtual_memory()
    print(f"Memory Usage: {memory.percent}%")
    return memory.percent

# Function to check the number of processes
def check_process_count():
    process_count = len(psutil.pids())
    print(f"Number of Processes: {process_count}")
    return process_count

# Function to log suspicious activity
def log_suspicious_activity(cpu_usage, process_count, memory_usage):
    with open("attack_log.txt", "a") as log_file:
        log_file.write(f"Suspicious Activity Detected - CPU: {cpu_usage}%, Processes: {process_count}, Memory: {memory_usage}%\n")
        log_file.flush()



# Function to kill processes (IPS action)
def kill_malicious_processes():
    print("Performing IPS: Killing malicious processes...")
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            # Skip processes that don't have CPU percent information
            if proc.info['cpu_percent'] is None:
                continue

            # Example: kill processes using too much CPU or system resources (e.g., fork bombs)
            if proc.info['cpu_percent'] > 50:  # You can adjust this threshold
                print(f"Killing process {proc.info['name']} with PID {proc.info['pid']}")
                proc.kill()  # Terminate the process
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

        

# Function to monitor the system continuously
def monitor_system():
    while True:
        # Check the system metrics
        cpu_usage = check_cpu_usage()
        process_count = check_process_count()
        memory_usage = check_memory_usage()

        # Detect anomalies
        if cpu_usage > CPU_THRESHOLD or process_count > PROCESS_THRESHOLD or memory_usage > 90:
            print("ALERT: Possible Attack Detected!")
            log_suspicious_activity(cpu_usage, process_count, memory_usage)

          # IPS action: Kill processes if attack is detected
            kill_malicious_processes()


        # Wait for a short time before checking again
time.sleep(2)  # Adjust sleep time as necessary

if __name__ == "__main__":
    print("Starting system monitoring...")
    monitor_system()
