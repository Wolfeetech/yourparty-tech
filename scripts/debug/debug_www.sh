#!/bin/bash
echo "Testing as www-data:"
su -s /bin/bash -c "php /var/www/html/test_db.php" www-data
echo ""
echo "Checking wp-config tail:"
tail -n 20 /var/www/html/wp-config.php
