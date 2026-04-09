import subprocess
import os
import sys

if len(sys.argv) < 3:
    print("Usage: python puller.py <remote_path_on_host> <local_dest>")
    exit(1)

remote_path = sys.argv[1]
local_dest = sys.argv[2]
dest_host = 'root@192.168.178.25'

print(f"Pulling {remote_path} from {dest_host} to {local_dest}...")

# Use ssh to cat the file and capture it locally
result = subprocess.run(['ssh', '-q', dest_host, f'cat {remote_path}'], capture_output=True)

if result.returncode == 0:
    with open(local_dest, 'wb') as f:
        f.write(result.stdout)
    print("✅ Successfully pulled file.")
else:
    print(f"❌ Failed to pull file. Return code: {result.returncode}")
    print(f"Error: {result.stderr.decode()}")
