#!/bin/bash
# Test Auto-DJ Integration
# Submits multiple votes to influence the mood

NONCE=$1
if [ -z "$NONCE" ]; then
    echo "Usage: $0 <nonce>"
    exit 1
fi

echo "Submitting 5 'energy' votes..."

for i in {1..5}; do
  curl -s -X POST "https://yourparty.tech/wp-json/yourparty/v1/vote-mood" \
    -H "Content-Type: application/json" \
    -H "X-WP-Nonce: $NONCE" \
    -d '{
      "song_id": "auto_dj_test_song",
      "mood_current": "neutral",
      "mood_next": "energy",
      "vote": "like"
    }'
  echo -n "."
done
echo "Done."
echo "Now watch logs for 'Dominant mood detected: energy'"
