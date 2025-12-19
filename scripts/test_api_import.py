#!/usr/bin/env python3
"""Test full api import."""
import sys
import os
os.chdir('/opt/radio-api')
sys.path.insert(0, '/opt/radio-api')

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
