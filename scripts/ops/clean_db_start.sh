#!/bin/bash
systemctl stop mariadb
rm -f /etc/mysql/mariadb.conf.d/50-server.cnf
cat > /etc/mysql/mariadb.conf.d/50-server.cnf << 'EOFCONFIG'
[mysqld]
bind-address = 0.0.0.0
innodb_use_native_aio = 0
innodb_flush_method = fsync
EOFCONFIG
systemctl start mariadb
sleep 3
systemctl is-active mariadb
mysql -e "CREATE DATABASE IF NOT EXISTS wordpress_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'wp_user'@'%' IDENTIFIED BY 'SimplePass123';"
mysql -e "GRANT ALL PRIVILEGES ON wordpress_db.* TO 'wp_user'@'%';"
mysql -e "FLUSH PRIVILEGES;"
echo "Database ready!"
