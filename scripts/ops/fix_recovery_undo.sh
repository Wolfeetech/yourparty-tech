#!/bin/bash
sed -i '/innodb_force_recovery/d' /etc/mysql/mariadb.conf.d/50-server.cnf
systemctl restart mariadb
sleep 3
systemctl is-active mariadb
