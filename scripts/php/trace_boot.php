<?php
echo "TRACE: Start\n";
define('WP_USE_THEMES', false);
define('WP_DEBUG', true);

echo "TRACE: Loading wp-config.php manual check\n";
if (file_exists('/var/www/html/wp-config.php')) echo "TRACE: wp-config exists\n";

echo "TRACE: Loading wp-load.php\n";
// We copy wp-load logic to trace it
define( 'ABSPATH', '/var/www/html/' );

echo "TRACE: Check error_reporting\n";
error_reporting( E_ALL );
ini_set( 'display_errors', 1 );

echo "TRACE: Requiring wp-includes/load.php\n";
require_once( ABSPATH . 'wp-includes/load.php' );

echo "TRACE: Requiring wp-includes/default-constants.php\n";
require_once( ABSPATH . 'wp-includes/default-constants.php' );

echo "TRACE: wp_initial_constants()\n";
wp_initial_constants();

echo "TRACE: Loading wp-config.php real\n";
require_once( ABSPATH . 'wp-config.php' );

echo "TRACE: Loading wp-settings.php\n";
require_once( ABSPATH . 'wp-settings.php' );

echo "TRACE: Success\n";
?>
