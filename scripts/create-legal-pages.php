<?php
/**
 * Create Impressum and Datenschutz pages
 * Run this once via: php create-legal-pages.php
 */

// Load WordPress
require_once('/var/www/html/wp-load.php');

echo "Creating legal pages...\n";

// Create Impressum page
$impressum = get_page_by_path('impressum');
if (!$impressum) {
    $id = wp_insert_post([
        'post_title' => 'Impressum',
        'post_name' => 'impressum',
        'post_status' => 'publish',
        'post_type' => 'page',
        'page_template' => 'page-impressum.php'
    ]);
    echo "Created Impressum page with ID: $id\n";
} else {
    // Update template if page exists
    update_post_meta($impressum->ID, '_wp_page_template', 'page-impressum.php');
    echo "Impressum already exists (ID: {$impressum->ID}), updated template.\n";
}

// Create Datenschutz page
$datenschutz = get_page_by_path('datenschutz');
if (!$datenschutz) {
    $id = wp_insert_post([
        'post_title' => 'Datenschutz',
        'post_name' => 'datenschutz',
        'post_status' => 'publish',
        'post_type' => 'page',
        'page_template' => 'page-datenschutz.php'
    ]);
    echo "Created Datenschutz page with ID: $id\n";
} else {
    // Update template if page exists
    update_post_meta($datenschutz->ID, '_wp_page_template', 'page-datenschutz.php');
    echo "Datenschutz already exists (ID: {$datenschutz->ID}), updated template.\n";
}

echo "Done!\n";
