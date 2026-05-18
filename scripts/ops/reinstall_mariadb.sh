#!/bin/bash
set -e
echo "=== Purging MariaDB ==="
systemctl stop mariadb || true
apt-get purge -y mariadb-server mariadb-client
rm -rf /var/lib/mysql /etc/mysql
apt-get autoremove -y
apt-get clean

echo "=== Installing fresh MariaDB ==="
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server

echo "=== Configuring MariaDB ==="
cat > /etc/mysql/mariadb.conf.d/50-server.cnf << 'EOF'
[mysqld]
bind-address = 0.0.0.0
innodb_use_native_aio = 0
innodb_flush_method = fsync
EOF

echo "=== Starting MariaDB ==="
systemctl start mariadb
systemctl enable mariadb
sleep 5

echo "=== Creating WordPress Database ==="
mysql -e "CREATE DATABASE wordpress_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER 'wp_user'@'%' IDENTIFIED BY 'SimplePass123';"
mysql -e "GRANT ALL PRIVILEGES ON wordpress_db.* TO 'wp_user'@'%';"
mysql -e "FLUSH PRIVILEGES;"

echo "=== DONE ==="
systemctl is-active mariadb
