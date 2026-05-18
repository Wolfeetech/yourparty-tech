#!/bin/bash
set -e

echo "=== Fixing MariaDB Configuration ==="
# Remove recovery mode
sed -i '/innodb_force_recovery/d' /etc/mysql/mariadb.conf.d/50-server.cnf
# Add LXC-friendly settings
cat >> /etc/mysql/mariadb.conf.d/50-server.cnf << 'EOF'
innodb_use_native_aio = 0
innodb_flush_method = fsync
EOF

echo "=== Restarting MariaDB ==="
systemctl restart mariadb
sleep 5

echo "=== Recreating WordPress Database ==="
mysql -e "DROP DATABASE IF EXISTS wordpress_db;"
mysql -e "CREATE DATABASE wordpress_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "DROP USER IF EXISTS 'wp_user'@'%';"
mysql -e "CREATE USER 'wp_user'@'%' IDENTIFIED BY 'SimplePass123';"
mysql -e "GRANT ALL PRIVILEGES ON wordpress_db.* TO 'wp_user'@'%';"
mysql -e "FLUSH PRIVILEGES;"

echo "=== Database Ready ==="
systemctl is-active mariadb
