<?php
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');
update_option('template', 'yourparty-tech');
update_option('stylesheet', 'yourparty-tech');
echo "Theme restored to yourparty-tech.\n";
?>
