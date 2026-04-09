#!/usr/bin/env python3
"""Fix RateRequest model and add client metadata fallback"""
import re

with open('/opt/yourparty-api/app/main.py', 'r') as f:
    content = f.read()

# Fix the broken line with escaped newlines
content = content.replace(
    r'class RateRequest(BaseModel):\n    title: Optional[str] = None\n    artist: Optional[str] = None',
    '''class RateRequest(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None'''
)

# Also try the actual pattern if it's different
old_pattern = '''class RateRequest(BaseModel):
    song_id: str
    vote: Optional[str] = None
    rating: Optional[int] = None'''

new_pattern = '''class RateRequest(BaseModel):
    song_id: str
    vote: Optional[str] = None
    rating: Optional[int] = None
    title: Optional[str] = None
    artist: Optional[str] = None'''

if old_pattern in content and 'title: Optional[str] = None' not in content:
    content = content.replace(old_pattern, new_pattern)
    print("Added title/artist fields to RateRequest model")

# Find the logging.warning line about "not found in nowplaying/history"
# and add fallback to use client-sent metadata
fallback_code = '''
                    else:
                        # FALLBACK: Use client-sent metadata if AzuraCast lookup failed
                        if rate_request.title and rate_request.title != 'Unknown':
                            client_metadata = {
                                "title": rate_request.title,
                                "artist": rate_request.artist or "Unknown"
                            }
                            if not existing_rating:
                                update["$setOnInsert"] = client_metadata
                            else:
                                update["$set"] = {
                                    k: v for k, v in client_metadata.items()
                                    if not existing_rating.get(k) or existing_rating.get(k) == "Unknown"
                                }
                            logging.info(f"Using client-sent metadata for song={song_id[:12]}...: {rate_request.title} - {rate_request.artist}")
                        else:
                            logging.warning(f"Song {song_id} not found in nowplaying/history and no client metadata - metadata will not be stored")'''

# Check if fallback already exists
if 'Using client-sent metadata' not in content:
    # Find the warning line and replace it
    old_warning = 'logging.warning(f"Song {song_id} not found in nowplaying/history - metadata will not be stored")'
    if old_warning in content:
        content = content.replace(
            '                    else:\n                        logging.warning(f"Song {song_id} not found in nowplaying/history - metadata will not be stored")',
            fallback_code
        )
        print("Added client metadata fallback")

with open('/opt/yourparty-api/app/main.py', 'w') as f:
    f.write(content)

print("Done - checking syntax...")
import py_compile
try:
    py_compile.compile('/opt/yourparty-api/app/main.py', doraise=True)
    print("Syntax OK!")
except py_compile.PyCompileError as e:
    print(f"Syntax error: {e}")
