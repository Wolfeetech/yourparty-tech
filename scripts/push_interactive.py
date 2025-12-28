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

# Use unique tmp filename
tmp_base = os.path.basename(source)
remote_tmp = f"{dest_path}.{tmp_base}.b64"

# Initialize the file
subprocess.run(['ssh', '-q', dest_host, f'printf "" > {remote_tmp}'])

# Chunk size (1KB)
chunk_size = 1024
for i in range(0, len(b64_data), chunk_size):
    chunk = b64_data[i:i+chunk_size]
    # Append chunk
    subprocess.run(['ssh', '-q', dest_host, f'printf "{chunk}" >> {remote_tmp}'])
    time.sleep(0.02) # Rate limit

# Decode on host
subprocess.run(['ssh', '-q', dest_host, f'base64 -d {remote_tmp} > {dest_path}'])
subprocess.run(['ssh', '-q', dest_host, f'rm -f {remote_tmp}'])

print("✅ Successfully pushed file to Host.")
