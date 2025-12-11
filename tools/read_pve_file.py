import subprocess
import json
import time
import sys
import re

PVE_HOST = "192.168.178.25"
VM_ID = "210"
REMOTE_FILE = "/etc/samba/smb.conf"

def run_ssh(cmd):
    full_cmd = f'ssh -i C:\\Users\\StudioPC\\.ssh\\id_ed25519 -o StrictHostKeyChecking=no root@{PVE_HOST} "{cmd}"'
    result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        raise Exception(f"SSH Error: {result.stderr}")
    return result.stdout.strip()

def get_file_content():
    print(f"Requesting cat {REMOTE_FILE} on VM {VM_ID}...")
    # 1. Start Exec
    # qm guest exec <vmid> -- <command>
    # Returns: {"pid": 1234}
    exec_cmd = f"qm guest exec {VM_ID} -- cat {REMOTE_FILE}"
    out = run_ssh(exec_cmd)
    
    try:
        # PVE 6/7/8 output might vary. Usually just the JSON.
        # Clean up any "PVE Host" banner
        json_str = re.search(r'(\{.*\})', out).group(1)
        data = json.loads(json_str)
        pid = data['pid']
    except Exception as e:
        print(f"Failed to parse exec start output: {out}")
        raise e
        
    print(f"Started process PID: {pid}. Waiting for completion...")
    
    # 2. Poll Status
    # qm guest exec-status <vmid> <pid>
    # Returns: {"exited": 1, "exitcode": 0, "out-data": "..."}
    for _ in range(10):
        time.sleep(1)
        status_cmd = f"qm guest exec-status {VM_ID} {pid}"
        out = run_ssh(status_cmd)
        
        try:
            json_str = re.search(r'(\{.*\})', out, re.DOTALL).group(1)
            status = json.loads(json_str)
            
            if status.get('exited') == 1:
                if status.get('exitcode') != 0:
                    print(f"Command failed with exit code {status.get('exitcode')}")
                    if 'err-data' in status:
                        print(f"Error: {status['err-data']}")
                    return None
                    
                return status.get('out-data', "")
        except Exception as e:
            print(f"Polling error: {e}. Raw: {out}")
            
    return None

if __name__ == "__main__":
    try:
        content = get_file_content()
        if content:
            print("\n--- FILE CONTENT ---\n")
            print(content)
            print("\n--------------------\n")
            
            # Extract Share Definitions
            shares = re.findall(r'^\[(.*?)\]', content, re.MULTILINE)
            print(f"Found Shares: {shares}")
        else:
            print("No content retrieved.")
    except Exception as e:
        print(f"Error: {e}")
