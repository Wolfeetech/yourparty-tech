<?php
define( 'DB_NAME', 'wordpress_db' );
define( 'DB_USER', 'wp_user' );
define( 'DB_PASSWORD', 'SimplePass123' );
define( 'DB_HOST', '192.168.178.228' );

$mysqli = new mysqli(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME);

if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error);
}

$query = "SELECT option_name, option_value FROM wp_options WHERE option_name IN ('siteurl', 'home', 'active_plugins')";
$result = $mysqli->query($query);

if ($result) {
    echo "Options Found: " . $result->num_rows . "\n";
    while ($row = $result->fetch_assoc()) {
        echo $row['option_name'] . " = " . $row['option_value'] . "\n";
    }
} else {
    echo "Error querying options: " . $mysqli->error;
}

$query_users = "SELECT COUNT(*) as count FROM wp_users";
$res_users = $mysqli->query($query_users);
if ($res_users) {
   $row = $res_users->fetch_assoc();
   echo "User Count: " . $row['count'] . "\n";
}

$mysqli->close();
?>
