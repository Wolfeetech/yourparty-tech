<?php
$content = file_get_contents('/var/www/html/wp-config.php');
// Simple regex to grab defines
function grab($key, $content) {
    if (preg_match("/define\(\s*['\"]" . $key . "['\"]\s*,\s*['\"](.+?)['\"]\s*\)/", $content, $m)) {
        return $m[1];
    }
    return 'MISSING';
}

echo "DB_NAME=" . grab('DB_NAME', $content) . "\n";
echo "DB_USER=" . grab('DB_USER', $content) . "\n";
echo "DB_PASSWORD=" . grab('DB_PASSWORD', $content) . "\n";
echo "DB_HOST=" . grab('DB_HOST', $content) . "\n";
?>
