#!/bin/bash
curl -s "https://radio.yourparty.tech/api/station/1/playlists" -k \
  -H "X-API-Key: 9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c" \
  | jq '.[] | {id, name, is_enabled, type}'
