<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

echo "<h1>Debug DB Connection</h1>";

$host = '192.168.178.228';
$user = 'wp_user';
$pass = 'SimplePass123';
$db   = 'wordpress_db';
$port = 3306;

echo "<p>Attempting connection to $host...</p>";

try {
    $mysqli = new mysqli($host, $user, $pass, $db, $port);
    if ($mysqli->connect_errno) {
        echo "<p style='color:red'>Failed to connect to MySQL: (" . $mysqli->connect_errno . ") " . $mysqli->connect_error . "</p>";
    } else {
        echo "<p style='color:green'>Success! Host info: " . $mysqli->host_info . "</p>";
        $mysqli->close();
    }
} catch (Exception $e) {
    echo "<p style='color:red'>Exception: " . $e->getMessage() . "</p>";
}
echo "<hr>";
phpinfo();
?>
