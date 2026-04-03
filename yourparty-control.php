<?php
/*
Plugin Name: YourParty Control
Description: Lightweight Admin API for Container Management & Logging.
Version: 1.0.0
Author: YourParty Tech
*/

add_action('rest_api_init', function () {
    // 1. Status Endpoint
    register_rest_route('yourparty/v1', '/control', [
        'methods'  => 'GET',
        'callback' => function () {
            // Log Request
            $log = date('c') . ' - Control endpoint accessed by ' . $_SERVER['REMOTE_ADDR'] . "\n";
            file_put_contents('/var/www/html/wp-content/uploads/control.log', $log, FILE_APPEND);
            
            return rest_ensure_response([
                'status' => 'online', 
                'timestamp' => time(),
                'service' => 'YourParty Control',
                'environment' => 'production'
            ]);
        },
        'permission_callback' => '__return_true',
    ]);
});
