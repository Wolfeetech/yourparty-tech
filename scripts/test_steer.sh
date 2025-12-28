#!/bin/bash
echo "Logging in to get token..."
TOKEN_JSON=$(curl -s -X POST http://localhost:8000/token -d "username=admin&password=admin")
TOKEN=$(echo $TOKEN_JSON | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token',''))")

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed! Response: $TOKEN_JSON"
    exit 1
fi

echo "✅ Token acquired. Triggering Steer..."
curl -s -X POST http://localhost:8000/control/steer \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"station_id": 1, "mode": "manual", "target": "chill"}'
echo -e "\nDone."
