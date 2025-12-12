#!/bin/bash
# Test Live Mood Voting functionality
# Simulates a frontend vote request

# 1. Test /vote-mood (POST)
echo "Testing /vote-mood endpoint..."
response=$(curl -s -X POST "https://yourparty.tech/wp-json/yourparty/v1/vote-mood" \
  -H "Content-Type: application/json" \
  -H "X-WP-Nonce: $1" \
  -d '{
    "song_id": "test_verification_song",
    "mood_current": "energetic",
    "mood_next": "chill",
    "vote": "like"
  }')

echo "Response: $response"

if [[ $response == *"success"* ]] || [[ $response == *"status"* ]]; then
  echo "✅ /vote-mood PASSED"
else
  echo "❌ /vote-mood FAILED"
  echo "Full Response: $response"
fi
