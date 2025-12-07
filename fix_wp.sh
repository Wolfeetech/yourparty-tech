#!/bin/bash
sed -i "s/192.168.178.25/192.168.178.228/g" /var/www/html/wp-config.php
echo "Fixed DB Host in wp-config.php"
