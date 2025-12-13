<?php
define( 'DB_NAME', 'wordpress_db' );
define( 'DB_USER', 'wp_user' );
define( 'DB_PASSWORD', 'SimplePass123' );
define( 'DB_HOST', '192.168.178.228' );

$mysqli = new mysqli(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME);

if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}

$result = $mysqli->query("SHOW TABLES");

if ($result) {
    echo "Tables in " . DB_NAME . ":\n";
    while ($row = $result->fetch_array()) {
        echo $row[0] . "\n";
    }
} else {
    echo "Error showing tables: " . $mysqli->error;
}
$mysqli->close();
?>
