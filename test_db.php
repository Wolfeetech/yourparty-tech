<?php
$mysqli = new mysqli("192.168.178.228", "wp_user", "SimplePass123", "wordpress_db");
if ($mysqli->connect_errno) {
    echo "Failed to connect to MySQL: (" . $mysqli->connect_errno . ") " . $mysqli->connect_error;
} else {
    echo "Success!";
}
?>
