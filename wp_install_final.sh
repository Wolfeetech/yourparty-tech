#!/bin/bash
cd /var/www/html
chmod +x /tmp/wp-cli.phar
php /tmp/wp-cli.phar db reset --yes --allow-root
php /tmp/wp-cli.phar core install \
  --url=https://yourparty.tech \
  --title="YourParty Radio" \
  --admin_user=admin \
  --admin_password=admin123 \
  --admin_email=admin@yourparty.tech \
  --skip-email \
  --allow-root
chown -R www-data:www-data /var/www/html
echo "WordPress installed successfully!"
