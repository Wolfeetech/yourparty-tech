import os
import sys
import subprocess
import webbrowser
import time
import urllib.request
import zipfile
import shutil
from pathlib import Path

# Configuration
FPCALC_URL = "https://github.com/acoustid/chromaprint/releases/download/v1.5.1/chromaprint-fpcalc-1.5.1-windows-x86_64.zip"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173
BASE_DIR = Path(__file__).parent

def install_requirements():
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_fpcalc():
    fpcalc_path = BASE_DIR / "fpcalc.exe"
    if not fpcalc_path.exists():
        print("fpcalc.exe not found. Downloading...")
        try:
            zip_path = BASE_DIR / "fpcalc.zip"
            urllib.request.urlretrieve(FPCALC_URL, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract only fpcalc.exe
                for file in zip_ref.namelist():
                    if file.endswith("fpcalc.exe"):
                        source = zip_ref.open(file)
                        target = open(fpcalc_path, "wb")
                        with source, target:
                            shutil.copyfileobj(source, target)
                        break
            
            os.remove(zip_path)
            print("fpcalc installed successfully.")
        except Exception as e:
            print(f"Failed to download fpcalc: {e}")
            print("Please download it manually from https://acoustid.org/chromaprint")

def start_backend():
    print("Starting Backend Server...")
    # Start uvicorn in a separate process
    return subprocess.Popen([sys.executable, "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)])

def start_frontend():
    print("Starting Frontend...")
    frontend_dir = BASE_DIR / "frontend"
    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        subprocess.check_call(["npm", "install"], cwd=frontend_dir, shell=True)
    
    return subprocess.Popen(["npm", "run", "dev"], cwd=frontend_dir, shell=True)

def main():
    print("=== Music Library Automation Setup ===")
    
    # 1. Setup Environment
    install_requirements()
    check_fpcalc()
    
    # 2. Start Services
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    print(f"Services started. Backend: {BACKEND_PORT}, Frontend: {FRONTEND_PORT}")
    print("Waiting for services to initialize...")
    time.sleep(5)
    
    # 3. Open Browser
    webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main()
