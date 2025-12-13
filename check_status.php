<?php
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');
echo "SITE_URL: " . get_option('siteurl') . "\n";
echo "HOME: " . get_option('home') . "\n";
echo "TEMPLATE: " . get_option('template') . "\n";
echo "STYLESHEET: " . get_option('stylesheet') . "\n";
echo "THEMES: " . implode(', ', array_keys(wp_get_themes())) . "\n";
?>
