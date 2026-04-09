<?php 
echo "STARTING WP LOAD...\n";
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');
echo "WP LOADED OK\n";
?>
