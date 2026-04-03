<?php
// /wp-content/themes/yourparty-tech/image-proxy.php
if (!isset($_GET['url'])) die();
$url = urldecode($_GET['url']);

// Security: Only allow internal domains
if (strpos($url, 'radio.yourparty.tech') === false && strpos($url, 'yourparty.tech') === false) die('Invalid Domain');

$path = parse_url($url, PHP_URL_PATH);
$ext = pathinfo($path, PATHINFO_EXTENSION);

$mime = 'image/jpeg';
if($ext === 'png') $mime = 'image/png';
if($ext === 'webp') $mime = 'image/webp';

header('Content-Type: ' . $mime);
header('Cache-Control: public, max-age=3600');
header('Access-Control-Allow-Origin: *'); // Allow usage in Canvas

// Stream with disabled SSL verification
$ctx = stream_context_create([
    "ssl" => [
        "verify_peer" => false,
        "verify_peer_name" => false,
    ],
    "http" => [
        "timeout" => 5
    ]
]);

$fp = @fopen($url, 'rb', false, $ctx);
if ($fp) {
    fpassthru($fp);
} else {
    http_response_code(404);
}
