#!/bin/bash
sed -i 's/innodb_force_recovery = 1/innodb_force_recovery = 3/' /etc/mysql/mariadb.conf.d/50-server.cnf
systemctl reset-failed mariadb
systemctl start mariadb
sleep 3
systemctl is-active mariadb
