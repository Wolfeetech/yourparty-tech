#!/bin/bash
echo "=== Container List ==="
for i in $(pct list | awk 'NR>1 {print $1}'); do
    name=$(pct config $i | grep hostname | cut -d: -f2 | tr -d ' ')
    size=$(lvs pve/vm-${i}-disk-0 --noheadings -o lv_size 2>/dev/null | tr -d ' ')
    status=$(pct status $i | grep status | cut -d: -f2 | tr -d ' ')
    echo "CT $i: $name ($size) - $status"
done
echo ""
echo "=== VM List ==="
for i in $(qm list | awk 'NR>1 {print $1}'); do
    name=$(qm config $i | grep name | head -1 | cut -d: -f2 | tr -d ' ')
    size=$(lvs pve/vm-${i}-disk-0 --noheadings -o lv_size 2>/dev/null | tr -d ' ')
    status=$(qm status $i | cut -d: -f2 | tr -d ' ')
    echo "VM $i: $name ($size) - $status"
done
echo ""
echo "=== Thin Pool Status ==="
lvs pve/data --noheadings -o lv_size,data_percent
