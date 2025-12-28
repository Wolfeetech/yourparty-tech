#!/bin/bash
# Test Rating & Mood API Endpoints

API_URL="https://api.yourparty.tech"

echo "=== 1. Get Current Status (Song ID) ==="
SONG_INFO=$(curl -s -k "$API_URL/status" | jq '.now_playing.song | {id, title, artist}')
echo "$SONG_INFO"
SONG_ID=$(echo "$SONG_INFO" | jq -r '.id')

echo ""
echo "=== 2. Test Rating Endpoint ==="
curl -s -k -X POST "$API_URL/rate" \
  -H "Content-Type: application/json" \
  -d "{\"song_id\": \"$SONG_ID\", \"rating\": 5}" | jq .

echo ""
echo "=== 3. Test Mood Tag Endpoint ==="
curl -s -k -X POST "$API_URL/mood-tag" \
  -H "Content-Type: application/json" \
  -d "{\"song_id\": \"$SONG_ID\", \"mood\": \"energetic\"}" | jq .

echo ""
echo "=== 4. Check MongoDB Data ==="
# This would need access to MongoDB - skip for now

echo ""
echo "=== 5. Check Current Steering State ==="
curl -s -k "$API_URL/control/steer" | jq .
