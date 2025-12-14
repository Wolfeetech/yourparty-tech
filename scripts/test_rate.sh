#!/bin/bash
# Test Rating Endpoint
curl -s -k -X POST "https://api.yourparty.tech/rate" \
  -H "Content-Type: application/json" \
  -d '{"song_id": "1dec559f48da6b32efb3adeb95f8964a", "rating": 5, "title": "Shake Your Groove Thing", "artist": "Peaches & Herb"}'
