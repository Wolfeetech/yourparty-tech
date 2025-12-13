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

define( 'WP_HOME', 'https://yourparty.tech' );
define( 'WP_SITEURL', 'https://yourparty.tech' );

// API Keys
define('YOURPARTY_AZURACAST_URL', 'http://192.168.178.210');
define('YOURPARTY_AZURACAST_API_KEY', '9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c');

define('FS_METHOD', 'direct');

$table_prefix = 'wp_';

if ( ! defined( 'ABSPATH' ) ) {
    define( 'ABSPATH', __DIR__ . '/' );
}
require_once ABSPATH . 'wp-settings.php';
