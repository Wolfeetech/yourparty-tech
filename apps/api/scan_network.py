
import socket
import threading
from queue import Queue

# Subnet to scan
SUBNET = "192.168.178."
PORT = 445 # SMB
TIMEOUT = 0.5

scan_queue = Queue()
found_hosts = []

def port_scan(target_ip):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        result = s.connect_ex((target_ip, PORT))
        if result == 0:
            try:
                hostname, _, _ = socket.gethostbyaddr(target_ip)
            except:
                hostname = "Unknown"
            print(f"✅ Found SMB Host: {target_ip} ({hostname})")
            found_hosts.append((target_ip, hostname))
        s.close()
    except:
        pass

def worker():
    while not scan_queue.empty():
        ip = scan_queue.get()
        port_scan(ip)
        scan_queue.task_done()

def scan_network():
    print(f"🚀 Scanning {SUBNET}0/24 for SMB (Port {PORT})...")
    
    # Populate Queue
    for i in range(1, 255):
        scan_queue.put(f"{SUBNET}{i}")

    # Threads
    for _ in range(20):
        t = threading.Thread(target=worker)
        t.start()

    scan_queue.join()
    print("🏁 Scan Complete.")
    
    if found_hosts:
        print("\n--- Detected SMB Servers ---")
        for ip, host in found_hosts:
            print(f"{ip} | {host}")
    else:
        print("No SMB hosts found.")

if __name__ == "__main__":
    scan_network()
