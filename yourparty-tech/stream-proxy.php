<?php
/**
 * YourParty Stream Proxy
 * Enables CORS for Audio Visualizer
 */

// Critical: Prevent PHP script timeout
set_time_limit(0);
// Close session just in case
if(session_id()) session_write_close();

error_reporting(0);

// Headers for CORS and Streaming
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header("Content-Type: audio/mpeg");
header("Cache-Control: no-cache, must-revalidate");
header("Pragma: no-cache");
header("Expires: 0");

// The stable stream URL
$target_url = 'https://radio.yourparty.tech/radio/8000/radio.mp3';

// Open Stream
$context = stream_context_create([
    'ssl' => [
        'verify_peer' => false,
        'verify_peer_name' => false,
    ],
    'http' => [
        'follow_location' => true,
        'timeout' => 15, // Connection timeout
        'user_agent' => 'YourPartyProxy/1.0'
    ]
]);

$fp = @fopen($target_url, 'rb', false, $context);

if ($fp) {
    // Disable output buffering
    while (ob_get_level()) ob_end_clean();
    
    // Pass through data
    fpassthru($fp);
    fclose($fp);
} else {
    header("HTTP/1.1 502 Bad Gateway");
    echo "Stream Source Unreachable";
}
exit;
