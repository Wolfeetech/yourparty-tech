<?php
/**
 * Stream Proxy - Simple version
 * Proxies AzuraCast stream through WordPress (valid SSL)
 */

// Disable error reporting to avoid corrupting stream
error_reporting(0);

// Stream URL (internal AzuraCast)
$stream_url = 'http://192.168.178.210/listen/radio.yourparty/radio.mp3';

// Headers
header('Access-Control-Allow-Origin: *');
header('Content-Type: audio/mpeg');
header('Cache-Control: no-cache');
header('X-Accel-Buffering: no'); // Disable nginx buffering

// Stream context
$context = stream_context_create([
    'http' => [
        'timeout' => 30,
        'follow_location' => true
    ]
]);

// Open stream
$fp = @fopen($stream_url, 'rb', false, $context);

if ($fp) {
    // Stream the audio
    fpassthru($fp);
    fclose($fp);
} else {
    header("HTTP/1.1 502 Bad Gateway");
    echo "Stream unavailable";
}
exit;
