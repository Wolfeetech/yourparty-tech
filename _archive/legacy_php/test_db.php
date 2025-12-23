<?php
$host = '192.168.178.228';
$user = 'wp_user';
$pass = 'SimplePass123';
$db   = 'wordpress_db';

echo "Attempting connection to $host with user $user...<br>";

$mysqli = new mysqli($host, $user, $pass, $db);

if ($mysqli->connect_error) {
    die('Connect Error (' . $mysqli->connect_errno . ') ' . $mysqli->connect_error);
}

echo 'Success... ' . $mysqli->host_info . "\n";
echo 'Server ' . $mysqli->server_info;
$mysqli->close();
?>
