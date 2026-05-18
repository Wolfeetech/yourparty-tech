#!/bin/bash
printf 'SimplePass123\nSimplePass123\n' | smbpasswd -a studio
cat <<EOT >> /etc/samba/smb.conf

[music]
   comment = YourParty Music Library
   path = /mnt/music_hdd
   browseable = yes
   read only = no
   guest ok = no
   valid users = studio
   create mask = 0775
   directory mask = 0775
   force user = wolfadmin
   force group = wolfadmin
EOT
systemctl restart smbd
