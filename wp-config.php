<?php
define( 'DB_NAME', 'wordpress_db' );
define( 'DB_USER', 'wp_user' );
define( 'DB_PASSWORD', 'SimplePass123' );
define( 'DB_HOST', '192.168.178.228' );
define( 'DB_CHARSET', 'utf8' );
define( 'DB_COLLATE', '' );

// Keys
define( 'AUTH_KEY',         'd89g7s89g7s98g7s98g7s98g7' );
define( 'SECURE_AUTH_KEY',  's89g7s98g7s98g7s98g7s98g7' );
define( 'LOGGED_IN_KEY',    'a89g7s98g7s98g7s98g7s98g7' );
define( 'NONCE_KEY',        'm89g7s98g7s98g7s98g7s98g7' );
define( 'AUTH_SALT',        'n89g7s98g7s98g7s98g7s98g7' );
define( 'SECURE_AUTH_SALT', 'b89g7s98g7s98g7s98g7s98g7' );
define( 'LOGGED_IN_SALT',   'v89g7s98g7s98g7s98g7s98g7' );
define( 'NONCE_SALT',       'c89g7s98g7s98g7s98g7s98g7' );

$table_prefix = 'wp_';

// DEBUGGING enabled
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', false ); // Force false to avoid HTML in CLI, logs only

// APP CONSTANTS
define('YOURPARTY_AZURACAST_URL', 'http://192.168.178.210');
define('YOURPARTY_AZURACAST_API_KEY', '9199dc63da623190:c9f8c3a22e25932753dd3f4d57fa0d9c');

define('FS_METHOD', 'direct');

if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}
require_once ABSPATH . 'wp-settings.php';
