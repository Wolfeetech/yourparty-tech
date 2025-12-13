<?php
echo "1. Start\n";
define( 'WP_DEBUG', true );
define( 'ABSPATH', '/var/www/html/' );

echo "2. Loading version.php\n";
require_once( ABSPATH . 'wp-includes/version.php' );

echo "3. Loading load.php\n";
require_once( ABSPATH . 'wp-includes/load.php' );

echo "4. Loading default-constants.php\n";
require_once( ABSPATH . 'wp-includes/default-constants.php' );

echo "5. Loading plugin.php\n";
require_once( ABSPATH . 'wp-includes/plugin.php' );

echo "6. Loading functions.php (Core)\n";
require_once( ABSPATH . 'wp-includes/functions.php' );

echo "7. Initializing Timer\n";
timer_start();

echo "8. Loading wp-config.php\n";
// Manually defining what wp-config does to verify DB constants
require_once( ABSPATH . 'wp-config.php' );

echo "9. Loading wp-db.php\n";
require_once( ABSPATH . 'wp-includes/wp-db.php' );

echo "10. Connecting DB\n";
if ( empty( $wpdb ) ) {
    $wpdb = new wpdb( DB_USER, DB_PASSWORD, DB_NAME, DB_HOST );
}

echo "11. DB Check: " . (empty($wpdb->error) ? 'OK' : $wpdb->error) . "\n";

echo "12. Loading wp-settings.php (Actual Bootstrap)\n";
require_once( ABSPATH . 'wp-settings.php' );

echo "13. SUCCESS: Bootstrap Complete\n";
?>
