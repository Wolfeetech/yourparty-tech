import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    import models.schemas
    print("SUCCESS: imported models.schemas")
except ImportError as e:
    print(f"ERROR: {e}")

try:
    from models.schemas import RatingRequest
    print("SUCCESS: imported RatingRequest")
except ImportError as e:
    print(f"ERROR: {e}")

# Check routers
try:
    import routers.library
    print("SUCCESS: imported routers.library")
except ImportError as e:
    print(f"ERROR: {e}")
