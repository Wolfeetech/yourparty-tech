<?php
/**
 * Stream Proxy Handler
 * Handles the logic for streaming radio content via WordPress routing.
 */

function yourparty_handle_stream_request() {
    // Configuration
    $url = 'http://192.168.178.210/listen/radio.yourparty/radio.mp3';
    
    // Headers
    if (function_exists('apache_setenv')) {
        apache_setenv('no-gzip', 1);
    }
    ini_set('zlib.output_compression', 'Off');
    
    header('Access-Control-Allow-Origin: *');
    header('Content-Type: audio/mpeg');
    header('Cache-Control: no-cache, no-store, must-revalidate');
    header('Pragma: no-cache');
    header('Expires: 0');

    // cURL Init
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, false); // Stream directly to output
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 5);
    curl_setopt($ch, CURLOPT_TIMEOUT, 0); // No timeout for stream
    curl_setopt($ch, CURLOPT_USERAGENT, 'YourParty-WP-Proxy/1.0');
    
    // Buffer handling
    curl_setopt($ch, CURLOPT_WRITEFUNCTION, function($ch, $data) {
        echo $data;
        flush(); // Flush to client immediately
        return strlen($data);
    });

    // Execute
    $success = curl_exec($ch);
    
    if (!$success) {
        error_log('Stream Proxy cURL Error: ' . curl_error($ch));
        status_header(502);
        echo "Stream unavailable";
    }

    curl_close($ch);
    exit;
}
