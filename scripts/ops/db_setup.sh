#!/bin/bash
set -e
sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf
systemctl restart mariadb
sleep 3
mysql -e "CREATE DATABASE wordpress_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER 'wp_user'@'192.168.178.%' IDENTIFIED BY 'SimplePass123';"
mysql -e "GRANT ALL PRIVILEGES ON wordpress_db.* TO 'wp_user'@'192.168.178.%';"
mysql -e "FLUSH PRIVILEGES;"
systemctl is-active mariadb
echo "Database ready!"
