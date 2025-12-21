<?php
/**
 * Stream Proxy for CORS support
 */

// Disable error reporting to avoid corrupting the stream
error_reporting(0);

// Target Stream URLs
// Load Configuration from JSON
$config_path = __DIR__ . '/../config/stream_targets.json';
$urls = [];

if (file_exists($config_path)) {
    $config_data = json_decode(file_get_contents($config_path), true);
    if (isset($config_data['targets']) && is_array($config_data['targets'])) {
        $urls = $config_data['targets'];
    }
}

// Fallback if config is missing (Safety net)
if (empty($urls)) {
    // Log error to server log
    error_log('Stream Proxy Error: Config file missing at ' . $config_path);
    header("HTTP/1.1 503 Service Unavailable");
    die('Stream configuration missing');
}

// Headers
header('Access-Control-Allow-Origin: *');
header('Content-Type: audio/mpeg');
header('Cache-Control: no-cache');

// Context options
$default_opts = [
    'ssl' => [
        'verify_peer' => false,
        'verify_peer_name' => false,
    ],
    'http' => [
        'follow_location' => true,
        'timeout' => 5 // Short timeout for internal
    ]
];

$fp = false;

foreach ($urls as $url) {
    if (strpos($url, 'https') === 0) {
        $default_opts['http']['timeout'] = 15; // Longer timeout for public
    }

    $context = stream_context_create($default_opts);
    $fp = @fopen($url, 'rb', false, $context);

    if ($fp)
        break; // Success
}

if ($fp) {
    fpassthru($fp);
    fclose($fp);
} else {
    // Both failed
    header("HTTP/1.1 502 Bad Gateway");
    echo "Stream unavailable";
}
exit;
