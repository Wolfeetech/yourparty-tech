#!/bin/bash
# Check MySQL users
mysql -e "SELECT User, Host FROM mysql.user WHERE User LIKE 'wp%';"

# Test connection from WordPress container
echo "Testing connection..."
mysql -u wp_user -pSimplePass123 -h 192.168.178.228 wordpress_db -e "SELECT 1;" 2>&1
