#!/usr/bin/env python3
"""
Patch get_tracks_for_playlist to query mood directly from tracks collection
"""
import sys
sys.path.insert(0, '/opt/radio-api')

# Read the file
with open('/opt/radio-api/mongo_client.py', 'r') as f:
    content = f.read()

# Old code pattern
old_code = '''if mood:
                # Find song_ids with this mood first
                if not hasattr(self, 'moods_collection'):
                    self.moods_collection = self.db["moods"]
                mood_docs = list(self.moods_collection.find({"mood": mood}, {"song_id": 1}))
                song_ids = list(set([d["song_id"] for d in mood_docs if d.get("song_id")]))
                query["song_id"] = {"$in": song_ids}'''

# New code - direct query on tracks
new_code = '''if mood:
                # Query mood directly on tracks collection (V2 fix)
                query["mood"] = mood'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('/opt/radio-api/mongo_client.py', 'w') as f:
        f.write(content)
    print("✅ Patched mongo_client.py successfully!")
else:
    print("⚠️ Pattern not found - file may already be patched or different")
