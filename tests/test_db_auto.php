<?php
$content = file_get_contents('/var/www/html/wp-config.php');
function g($k, $c) { preg_match("/define\(\s*['\"]" . $k . "['\"]\s*,\s*['\"](.+?)['\"]\s*\)/", $c, $m); return $m[1]??''; }
$host = g('DB_HOST', $content);
$user = g('DB_USER', $content);
$pass = g('DB_PASSWORD', $content);
$name = g('DB_NAME', $content);

echo "TESTING DB: $user@$host (DB: $name)...\n";
$mysqli = new mysqli($host, $user, $pass, $name);
if ($mysqli->connect_error) {
    die("CONNECTION FAILED: " . $mysqli->connect_error . "\n");
}
echo "CONNECTION SUCCESS!\n";
$mysqli->close();
?>
