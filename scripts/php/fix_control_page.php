<?php
// fix_control_page.php RE-RUN
define('WP_USE_THEMES', false);
require('/var/www/html/wp-load.php');

$slug = 'control';
$title = 'Control Dashboard';
$template = 'templates/page-control.php';

$page = get_page_by_path($slug);
$page_id = 0;

if ($page) {
    echo "Page '$slug' exists (ID: {$page->ID}).\n";
    $page_id = $page->ID;
} else {
    echo "Page '$slug' NOT FOUND. Creating...\n";
    $page_id = wp_insert_post([
        'post_title'    => $title,
        'post_name'     => $slug,
        'post_type'     => 'page',
        'post_status'   => 'publish',
        'post_content'  => '',
        'post_author'   => 1
    ]);
    if (is_wp_error($page_id)) {
        die("Error creating page: " . $page_id->get_error_message());
    }
    echo "Page created (ID: $page_id).\n";
}

// FORCE TEMPLATE
$current_template = get_post_meta($page_id, '_wp_page_template', true);
echo "Current Template: " . var_export($current_template, true) . "\n";

if ($current_template !== $template) {
    update_post_meta($page_id, '_wp_page_template', $template);
    echo "UPDATED Template to: $template\n";
} else {
    echo "Template is already correct.\n";
}

// FORCE PERMALINK FLUSH
global $wp_rewrite;
$wp_rewrite->set_permalink_structure('/%postname%/');
flush_rewrite_rules();
echo "Permalinks flushed.\n";
