#!/bin/bash
rm -f /var/www/html/wp-config.php
cat <<EOF > /var/www/html/wp-config.php
<?php
define( 'DB_NAME', 'wordpress_db' );
define( 'DB_USER', 'wp_user' );
define( 'DB_PASSWORD', 'SimplePass123' );
define( 'DB_HOST', '192.168.178.228' );
define( 'DB_CHARSET', 'utf8' );
define( 'DB_COLLATE', '' );

define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', false );

if ( ! defined( 'ABSPATH' ) ) {
    define( 'ABSPATH', __DIR__ . '/' );
}
require_once ABSPATH . 'wp-settings.php';
EOF
chown www-data:www-data /var/www/html/wp-config.php
echo "Config created successfully."
