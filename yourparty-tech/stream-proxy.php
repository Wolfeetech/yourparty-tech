<?php
/**
 * Stream Proxy for CORS support
 */

// Disable error reporting to avoid corrupting the stream
error_reporting(0);

// Target Stream URLs
$urls = [
    'http://192.168.178.210/listen/radio.yourparty/radio.mp3', // AzuraCast (Primary)
    'http://192.168.178.206:8000/stream', // Custom Engine (Fallback)
    'https://radio.yourparty.tech/listen/radio.yourparty/radio.mp3' // Public DNS
];

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
