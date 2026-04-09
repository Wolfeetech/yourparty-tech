#!/bin/bash
# Professional AzuraCast Station Start Script
# Direct docker-compose and database approach

echo "============================================================"
echo "AzuraCast Station Startup - Direct Docker Access"
echo "============================================================"

# Get into the AzuraCast environment
cd /var/azuracast

echo ""
echo "[1/5] Checking AzuraCast containers..."
docker compose ps

echo ""
echo "[2/5] Restarting station services..."
docker compose restart stations

echo ""
echo "[3/5] Waiting for services to initialize..."
sleep 15

echo ""
echo "[4/5] Checking station status..."
docker compose exec -T web php /var/azuracast/www/bin/console azuracast:station-queues

echo ""
echo "[5/5] Verifying now-playing..."
curl -s -k https://192.168.178.210/api/nowplaying/1 | grep -o '"title":"[^"]*"' | head -1

echo ""
echo "============================================================"
echo "Startup complete. Check https://192.168.178.210/"
echo "============================================================"
