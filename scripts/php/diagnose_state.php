<?php
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

echo "Active Template: " . get_option('template') . "\n";
echo "Active Stylesheet: " . get_option('stylesheet') . "\n";
echo "Site URL: " . get_option('siteurl') . "\n";
echo "Home URL: " . get_option('home') . "\n";

echo "Root index.php exists: " . (file_exists('/var/www/html/index.php') ? 'YES' : 'NO') . "\n";
echo "Theme Dir exists: " . (is_dir('/var/www/html/wp-content/themes/' . get_option('stylesheet')) ? 'YES' : 'NO') . "\n";
?>
