<?php
/**
 * Stream Proxy Handler
 * Handles the logic for streaming radio content via WordPress routing.
 */

function yourparty_handle_stream_request() {
    // 1. Load Configuration
    // Path: theme/inc -> theme -> repo -> config
    $config_path = __DIR__ . '/../../config/stream_targets.json';
    $urls = [];

    if (file_exists($config_path)) {
        $config_content = file_get_contents($config_path);
        if ($config_content) {
            $config_data = json_decode($config_content, true);
            if (isset($config_data['targets']) && is_array($config_data['targets'])) {
                $urls = $config_data['targets'];
            }
        }
    }

    // 2. Safety Fallback
    if (empty($urls)) {
        error_log('Stream Proxy Error: Config missing or empty at ' . $config_path);
        status_header(503);
        echo 'Stream configuration missing';
        exit;
    }

    // 3. Header Setup
    // Disable buffering
    if (function_exists('apache_setenv')) {
        apache_setenv('no-gzip', 1);
    }
    ini_set('zlib.output_compression', 'Off');
    
    // Headers for streaming
    header('Access-Control-Allow-Origin: *');
    header('Content-Type: audio/mpeg');
    header('Cache-Control: no-cache, no-store, must-revalidate');
    header('Pragma: no-cache');
    header('Expires: 0');

    // 4. Connection Logic
    $default_opts = [
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
        ],
        'http' => [
            'follow_location' => true,
            'timeout' => 5 // Fast failover
        ]
    ];

    $fp = false;
    foreach ($urls as $url) {
        if (strpos($url, 'https') === 0) {
            $default_opts['http']['timeout'] = 15; // Longer for public
        }

        $context = stream_context_create($default_opts);
        $fp = @fopen($url, 'rb', false, $context);

        if ($fp) {
            // Success - double check we actually got data? 
            // fopen usually returns resource if connection opens.
            // We can check headers if needed, but for MP3 stream, just start piping.
            break; 
        }
    }

    // 5. Output
    if ($fp) {
        // Output loop
        while (!feof($fp)) {
            echo fread($fp, 8192);
            flush();
        }
        fclose($fp);
    } else {
        status_header(502);
        echo "Stream unavailable";
    }
    
    exit;
}
