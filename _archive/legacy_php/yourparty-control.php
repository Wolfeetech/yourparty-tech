<?php
/**
 * Plugin Name: YourParty Control
 * Description: Lightweight admin endpoint for container status and control logging.
 * Version: 1.0
 */

if (!defined('ABSPATH')) exit;

add_action('rest_api_init', function () {
    register_rest_route('yourparty/v1', '/control', [
        'methods' => 'GET',
        'callback' => 'yourparty_get_system_status',
        'permission_callback' => function () {
            return current_user_can('manage_options');
        }
    ]);
});

function yourparty_get_system_status() {
    // Attempt to read status file injected by host
    $status_file = '/var/www/html/server_status.json';
    
    if (file_exists($status_file)) {
        $data = json_decode(file_get_contents($status_file), true);
        yourparty_log_control_action('get_status', 'Status retrieved via API');
        return rest_ensure_response($data);
    }
    
    return new WP_Error('no_status', 'Status info unavailable', ['status' => 503]);
}

function yourparty_log_control_action($action, $details = '') {
    $log_file = WP_CONTENT_DIR . '/uploads/yourparty_control.log';
    $timestamp = date('Y-m-d H:i:s');
    $entry = "[$timestamp] [$action] $details" . PHP_EOL;
    file_put_contents($log_file, $entry, FILE_APPEND);
}
