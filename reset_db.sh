#!/bin/bash
set -e
echo "Stopping MariaDB..."
systemctl stop mariadb
echo "Backing up old data..."
mv /var/lib/mysql /var/lib/mysql.bak.$(date +%s)
mkdir /var/lib/mysql
chown mysql:mysql /var/lib/mysql
echo "Removing Recovery Mode..."
sed -i '/innodb_force_recovery/d' /etc/mysql/mariadb.conf.d/50-server.cnf
echo "Initializing new DB..."
mysql_install_db --user=mysql --datadir=/var/lib/mysql > /dev/null 2>&1
echo "Starting MariaDB..."
systemctl start mariadb
echo "Waiting for startup..."
sleep 5
systemctl is-active mariadb
echo "DB Reset Complete."
