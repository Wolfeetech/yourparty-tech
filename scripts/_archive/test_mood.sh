#!/bin/bash
# Test Mood Tag Endpoint
curl -s -k -X POST "https://api.yourparty.tech/mood-tag" \
  -H "Content-Type: application/json" \
  -d '{"song_id": "1dec559f48da6b32efb3adeb95f8964a", "mood": "groovy", "title": "Shake Your Groove Thing", "artist": "Peaches & Herb"}'
