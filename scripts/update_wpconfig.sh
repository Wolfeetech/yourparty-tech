#!/bin/bash
sed -i 's/SimplePass123/YpRd!2024#SecureDB/g' /var/www/html/wp-config.php
grep DB_PASSWORD /var/www/html/wp-config.php
