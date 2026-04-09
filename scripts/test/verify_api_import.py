import sys
import os

# Add apps/api to path so we can emulate running from that dir
api_path = os.path.join(os.getcwd(), 'apps', 'api')
sys.path.insert(0, api_path)

print(f"Added {api_path} to sys.path")
print("Attempting to import api...")

try:
    from api import app
    print("✅ SUCCESS: api imported correctly.")
    print(f"Routes found: {len(app.routes)}")
    for route in app.routes:
        print(f"  - {route.path} [{route.name}]")
except Exception as e:
    print(f"❌ FAILURE: Import failed with error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
