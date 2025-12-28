#!/bin/bash
# Test Vote Endpoint
curl -s -k -X POST "https://api.yourparty.tech/vote-next" \
  -H "Content-Type: application/json" \
  -H "Origin: https://yourparty.tech" \
  -d '{"vote": "energetic"}'
