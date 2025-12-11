#!/bin/bash
# Check if AzuraCast has a "request next song" or "skip" API
echo "=== Station Backend Info ==="
curl -s "https://radio.yourparty.tech/api/station/1" -k \
  -H "X-API-Key: 9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c" \
  | jq '{backend, backend_config}'

echo ""
echo "=== Check if AutoDJ can be controlled ==="
curl -s "https://radio.yourparty.tech/api/station/1/queue" -k \
  -H "X-API-Key: 9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c" \
  | jq '.[0:3]'
