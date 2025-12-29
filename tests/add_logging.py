#!/usr/bin/env python3
"""
Patch mongo_client.py to add debug logging
"""
import sys

TARGET = '/opt/radio-api/mongo_client.py'

try:
    with open(TARGET, 'r') as f:
        lines = f.readlines()

    new_lines = []
    patched = False
    
    for line in lines:
        new_lines.append(line)
        if 'query["mood"] = mood' in line and not 'logger.info' in line:
            indent = line[:line.find('query')]
            new_lines.append(f'{indent}logger.info(f"DEBUG PLAYLIST: Searching for mood={{mood}} query={{query}}")\n')
            patched = True
            
        if 'tracks = list(self.tracks_collection.find' in line:
             # Find indentation
             indent = line[:line.find('tracks')]
        
        if 'return [int(t["azuracast_id"])' in line and not 'logger.info' in line and patched:
             indent = line[:line.find('return')]
             new_lines.append(f'{indent}logger.info(f"DEBUG PLAYLIST: Found {{len(tracks)}} tracks")\n')

    if patched:
        with open(TARGET, 'w') as f:
            f.writelines(new_lines)
        print("✅ Added debug logging to mongo_client.py")
    else:
        print("⚠️  Could not find patch location or already patched")

except Exception as e:
    print(f"❌ Error: {e}")
