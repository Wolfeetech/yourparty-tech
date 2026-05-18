#!/bin/bash
cd /var/www/html
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
php wp-cli.phar db reset --yes --allow-root
php wp-cli.phar core install \
  --url=https://yourparty.tech \
  --title="YourParty Radio" \
  --admin_user=admin \
  --admin_password=admin123 \
  --admin_email=admin@yourparty.tech \
  --skip-email \
  --allow-root
echo "WordPress installed successfully!"
