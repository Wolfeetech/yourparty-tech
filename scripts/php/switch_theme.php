<?php
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');
update_option('template', 'twentytwentyfour');
update_option('stylesheet', 'twentytwentyfour');
update_option('current_theme', 'Twenty Twenty-Four');
echo "Theme switched to Twenty Twenty-Four.\n";
?>
