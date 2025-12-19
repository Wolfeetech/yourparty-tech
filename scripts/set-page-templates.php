<?php
/**
 * Set correct templates for Impressum and Datenschutz pages
 */
require_once('/var/www/html/wp-load.php');

echo "Setting page templates...\n";

// Get Impressum page
$impressum = get_page_by_path('impressum');
if ($impressum) {
    update_post_meta($impressum->ID, '_wp_page_template', 'page-impressum.php');
    echo "Set Impressum template (ID: {$impressum->ID})\n";
} else {
    echo "ERROR: Impressum page not found!\n";
}

// Get Datenschutz page
$datenschutz = get_page_by_path('datenschutz');
if ($datenschutz) {
    update_post_meta($datenschutz->ID, '_wp_page_template', 'page-datenschutz.php');
    echo "Set Datenschutz template (ID: {$datenschutz->ID})\n";
} else {
    echo "ERROR: Datenschutz page not found!\n";
}

echo "Done!\n";
