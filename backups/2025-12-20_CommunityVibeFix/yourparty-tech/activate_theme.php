<?php
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

$theme_slug = 'yourparty-tech';
$current = wp_get_theme();

echo "Current Theme: " . $current->get('Name') . "\n";

if ($current->get_stylesheet() !== $theme_slug) {
    echo "Switching to $theme_slug...\n";
    switch_theme($theme_slug);
    echo "Theme switched!\n";
} else {
    echo "Theme is already active.\n";
}

$new = wp_get_theme();
echo "New Theme: " . $new->get('Name') . "\n";
