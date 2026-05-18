#!/bin/bash
echo "=== Container Disk Usage ==="
for i in 100 101 103 108 109 110 120 130 202 207 208 211; do
    name=$(pct config $i 2>/dev/null | grep hostname | cut -d: -f2 | tr -d ' ')
    if [ -z "$name" ]; then continue; fi
    
    total=$(pct config $i 2>/dev/null | grep rootfs | grep -oP 'size=\K[0-9]+')
    used=$(pct exec $i -- df -h / 2>/dev/null | tail -1 | awk '{print $3}')
    pct_used=$(pct exec $i -- df -h / 2>/dev/null | tail -1 | awk '{print $5}')
    
    echo "CT $i ($name): $used used of ${total}G ($pct_used)"
done

echo ""
echo "=== Thin Pool Status ==="
lvs pve/data --noheadings -o lv_size,data_percent
