echo '/mnt/music_hdd 192.168.178.0/24(rw,sync,no_subtree_check,no_root_squash)' > /etc/exports
exportfs -a
systemctl restart nfs-kernel-server
