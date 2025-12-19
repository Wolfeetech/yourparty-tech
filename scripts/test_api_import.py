#!/usr/bin/env python3
"""Test full api import."""
import sys
import os
# Adjust path for local execution (Windows)
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
print(f"Adding to sys.path: {backend_path}")
sys.path.insert(0, backend_path)
os.chdir(backend_path)

# Load env
from dotenv import load_dotenv
load_dotenv()

print("Testing full api.py import...")
try:
    import api
    print(f"SUCCESS!")
    print(f"Has app: {hasattr(api, 'app')}")
    if hasattr(api, 'app'):
        print(f"app = {api.app}")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
