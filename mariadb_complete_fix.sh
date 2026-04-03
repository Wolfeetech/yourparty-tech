#!/bin/bash
set -e
echo "=== Creating clean MariaDB config ==="
cat > /etc/mysql/mariadb.conf.d/50-server.cnf << 'EOF'
[mysqld]
user = mysql
pid-file = /run/mysqld/mysqld.pid
basedir = /usr
datadir = /var/lib/mysql
tmpdir = /tmp
bind-address = 0.0.0.0
innodb_use_native_aio = 0
innodb_flush_method = fsync
max_connections = 100
connect_timeout = 5
wait_timeout = 600
max_allowed_packet = 64M
thread_cache_size = 128
sort_buffer_size = 4M
bulk_insert_buffer_size = 16M
tmp_table_size = 32M
max_heap_table_size = 32M
myisam_recover_options = BACKUP
key_buffer_size = 128M
table_open_cache = 400
myisam_sort_buffer_size = 512M
concurrent_insert = 2
read_buffer_size = 2M
read_rnd_buffer_size = 1M
query_cache_limit = 128K
query_cache_size = 64M
log_warnings = 2
slow_query_log_file = /var/log/mysql/mariadb-slow.log
long_query_time = 10
expire_logs_days = 10
max_binlog_size = 100M
default_storage_engine = InnoDB
innodb_buffer_pool_size = 256M
innodb_log_buffer_size = 8M
innodb_file_per_table = 1
innodb_open_files = 400
innodb_io_capacity = 400
innodb_flush_log_at_trx_commit = 1
EOF

echo "=== Ensuring correct permissions ==="
chown -R mysql:mysql /var/lib/mysql
chmod 755 /var/lib/mysql

echo "=== Starting MariaDB ==="
systemctl start mariadb
sleep 5
systemctl is-active mariadb

echo "=== Creating database ==="
mysql -e "CREATE DATABASE IF NOT EXISTS wordpress_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'wp_user'@'%' IDENTIFIED BY 'SimplePass123';"
mysql -e "GRANT ALL PRIVILEGES ON wordpress_db.* TO 'wp_user'@'%';"
mysql -e "FLUSH PRIVILEGES;"

echo "=== DONE ==="
