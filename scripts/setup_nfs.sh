qm guest exec 210 -- bash -c "echo '/mnt/music_hdd 192.168.178.211(rw,sync,no_subtree_check,no_root_squash)' | tee /etc/exports"
qm guest exec 210 -- exportfs -a
qm guest exec 210 -- systemctl restart nfs-kernel-server
