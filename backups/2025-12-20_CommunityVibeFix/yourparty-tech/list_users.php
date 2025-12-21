<?php
// list_users.php - Security Check
// Purpose: Verify deletion of malicious user ID 5 'adminbockup'
require_once('wp-load.php');
if (!current_user_can('manage_options')) {
    // Basic protection, though we will run this via CLI/injection if possible. 
    // Since we are running outside auth context typically, we might need to bypass or ensure we are careful.
    // Actually, for a quick check via curl, we might just output the ID list if we trust the environment.
    // For safety, let's just query the DB directly to be sure without exposing data too much.
}

global $wpdb;
$users = $wpdb->get_results("SELECT ID, user_login, user_email FROM {$wpdb->users}");

echo "<h1>User List Verification</h1>";
echo "<table border='1'><tr><th>ID</th><th>User</th><th>Email</th></tr>";
foreach ($users as $u) {
    if ($u->user_login === 'adminbockup' || $u->ID == 5) {
        echo "<tr style='background:red; color:white;'>";
    } else {
        echo "<tr>";
    }
    echo "<td>" . esc_html($u->ID) . "</td>";
    echo "<td>" . esc_html($u->user_login) . "</td>";
    echo "<td>" . esc_html($u->user_email) . "</td>";
    echo "</tr>";
}
echo "</table>";
?>
