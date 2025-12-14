<?php
define( 'WP_DEBUG', true );
define( 'ABSPATH', '/var/www/html/' );

echo "1. Loading version.php\n";
require_once( ABSPATH . 'wp-includes/version.php' );

echo "2. Loading load.php\n";
require_once( ABSPATH . 'wp-includes/load.php' );

echo "3. Loading default-constants.php\n";
require_once( ABSPATH . 'wp-includes/default-constants.php' );

echo "4. Executing wp_initial_constants()\n";
wp_initial_constants();

echo "5. Loading plugin.php\n";
require_once( ABSPATH . 'wp-includes/plugin.php' );

echo "6. Loading functions.php\n";
require_once( ABSPATH . 'wp-includes/functions.php' );

echo "7. Loading class-wp-error.php\n";
require_once( ABSPATH . 'wp-includes/class-wp-error.php' );

echo "8. Checking PHP/MySQL Versions\n";
wp_check_php_mysql_versions();

echo "9. Loading wp-config.php (Simulated)\n";
// Skip actual require since we defined everything manually above, 
// BUT we need DB creds. Let's just define them here to verify DB lib works.
define( 'DB_NAME', 'wordpress_db' );
define( 'DB_USER', 'wp_user' );
define( 'DB_PASSWORD', 'SimplePass123' );
define( 'DB_HOST', '192.168.178.228' );

echo "10. Loading wp-db.php\n";
require_once( ABSPATH . 'wp-includes/wp-db.php' );

echo "11. Init $wpdb\n";
require_once( ABSPATH . 'wp-includes/wp-db.php' );
if ( empty( $wpdb ) ) {
    $wpdb = new wpdb( DB_USER, DB_PASSWORD, DB_NAME, DB_HOST );
}

echo "12. Loading wp-settings complete emulation. SUCCESS.\n";
?>
