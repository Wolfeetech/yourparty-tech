#!/bin/bash
# Enable Recovery Mode
echo "innodb_force_recovery = 1" >> /etc/mysql/mariadb.conf.d/50-server.cnf
systemctl start mariadb
sleep 3
systemctl is-active mariadb
