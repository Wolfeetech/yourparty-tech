<?php
$conn = mysqli_connect("192.168.178.228", "wp_user", "SimplePass123", "wordpress_db");
if ($conn) {
    echo "SUCCESS: Connected to database\n";
    mysqli_close($conn);
} else {
    echo "FAILED: " . mysqli_connect_error() . "\n";
}
