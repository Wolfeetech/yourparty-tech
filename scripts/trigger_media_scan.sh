#!/bin/bash
# Trigger AzuraCast Media Scan for station "yourparty" (VM 210)

echo "Starting media scan for yourparty station..."
qm guest exec 210 -- bash -c 'cd /var/azuracast && docker compose exec -T web azuracast_cli media:reprocess yourparty'
echo "Media scan command sent."
echo ""
echo "Restarting station to apply changes..."
qm guest exec 210 -- bash -c 'cd /var/azuracast && docker compose exec -T web azuracast_cli station:restart yourparty'
echo "Station restart command sent."
echo ""
echo "Waiting 10 seconds for station to come online..."
sleep 10
echo "Done. Check if station is playing:"
echo "curl -s -k https://192.168.178.210/api/nowplaying/1 | grep -o '\"title\":\"[^\"]*\"'"
