import os
from datetime import timedelta
from dotenv import load_dotenv

# Load env
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, '.env'))

from auth import create_access_token, get_user, users_db, SECRET_KEY, ALGORITHM

print(f"DEBUG: SECRET_KEY={SECRET_KEY[:8]}...")
print(f"DEBUG: ALGORITHM={ALGORITHM}")
print(f"DEBUG: users_db keys={list(users_db.keys())}")

# 1. Create Token
token = create_access_token(data={"sub": "admin"})
print(f"DEBUG: Generated Token={token[:20]}...")

# 2. Validate Token (Mocking jwt.decode directly)
from jose import jwt
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    print(f"DEBUG: Decoded Username={username}")
    user = get_user(users_db, username)
    if user:
        print("✅ AUTH LOGIC SUCCESS: User found.")
    else:
        print("❌ AUTH LOGIC FAILURE: User NOT found in DB.")
except Exception as e:
    print(f"❌ AUTH LOGIC FAILURE: {e}")
