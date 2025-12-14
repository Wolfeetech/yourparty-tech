#!/usr/bin/env python3
import subprocess
import json
import time
import os

# Configuration
WP_UPLOAD_DIR = "/mnt/data_family/proxmox_backups/207/var/www/html/wp-content/uploads"
OUTPUT_FILE = os.path.join(WP_UPLOAD_DIR, "pve_status.json")

def cmd(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

def get_storage():
    # Parse pvesm status
    # Name             Type     Status     Total (KiB)      Used (KiB) Available (KiB)        %
    raw = cmd("pvesm status")
    lines = raw.split('\n')
    storage = []
    if len(lines) > 1:
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 7:
                storage.append({
                    "name": parts[0],
                    "type": parts[1],
                    "status": parts[2],
                    "total": parts[3],
                    "used": parts[4],
                    "percent": parts[6]
                })
    return storage

def get_containers():
    # Parse pct list
    # VMID       Status     Lock         Name
    raw = cmd("pct list")
    lines = raw.split('\n')
    containers = []
    if len(lines) > 1:
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 2:
                containers.append({
                    "vmid": parts[0],
                    "status": parts[1],
                    "name": parts[3] if len(parts) > 3 else "unknown"
                })
    return containers

def main():
    data = {
        "timestamp": time.time(),
        "storage": get_storage(),
        "containers": get_containers()
    }
    
    # Ensure directory exists (it should if 207 is mounted)
    if os.path.exists(WP_UPLOAD_DIR):
        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Status written to {OUTPUT_FILE}")
    else:
        print(f"Error: Target directory {WP_UPLOAD_DIR} does not exist.")

if __name__ == "__main__":
    main()
