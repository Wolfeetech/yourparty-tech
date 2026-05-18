#!/bin/bash
mysql -e "GRANT ALL PRIVILEGES ON wordpress_db.* TO 'wp_user'@'192.168.178.%' IDENTIFIED BY 'SimplePass123'; FLUSH PRIVILEGES;"
echo "Permissions Granted."
