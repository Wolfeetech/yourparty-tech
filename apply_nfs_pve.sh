#!/bin/bash
# Payload to run inside the guest
PAYLOAD="echo '/mnt/music_hdd 192.168.178.0/24(rw,sync,no_subtree_check,no_root_squash)' > /etc/exports && exportfs -a && systemctl restart nfs-kernel-server"
# Execute via qm guest exec
qm guest exec 210 -- bash -c "$PAYLOAD"
