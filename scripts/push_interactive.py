import subprocess
import os

import sys

if len(sys.argv) < 3:
    print("Usage: python pusher.py <source> <dest_path_on_host>")
    exit(1)

source = sys.argv[1]
dest_host = 'root@192.168.178.25'
dest_path = sys.argv[2]

if not os.path.exists(source):
    print(f"Source {source} not found!")
    exit(1)

import base64
import time

print(f"Pushing {source} to {dest_host}:{dest_path}...")
with open(source, 'rb') as f:
    # Use base64 to avoid character issues
    b64_data = base64.b64encode(f.read().replace(b'\r\n', b'\n')).decode('ascii')

# Initialize the file
subprocess.run(['ssh', '-q', dest_host, f'printf "" > {dest_path}.b64'])

# Chunk size (1KB)
chunk_size = 1024
for i in range(0, len(b64_data), chunk_size):
    chunk = b64_data[i:i+chunk_size]
    # Append chunk
    subprocess.run(['ssh', '-q', dest_host, f'printf "{chunk}" >> {dest_path}.b64'])
    time.sleep(0.05) # Rate limit

# Decode on host
subprocess.run(['ssh', '-q', dest_host, f'base64 -d {dest_path}.b64 > {dest_path}'])

print("✅ Successfully pushed file to Host.")
