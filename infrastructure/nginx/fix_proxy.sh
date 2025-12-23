#!/bin/bash
pct exec 103 -- docker exec npm sed -i 's/set $server .*/set $server "192.168.178.211";/' /data/nginx/proxy_host/8.conf
pct exec 103 -- docker exec npm sed -i 's/set $port .*/set $port 8000;/' /data/nginx/proxy_host/8.conf
pct exec 103 -- docker exec npm nginx -s reload
echo "Reconfigured 8.conf to -> 192.168.178.211:8000"
