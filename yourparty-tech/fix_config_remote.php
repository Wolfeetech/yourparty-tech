<?php
// fix_config_remote.php
// Purpose: Fix wp-config.php password mismatch ensuring site restoration.
// Authorized by User Request to "Restore Database Connection".

$config_path = '/var/www/html/wp-config.php';
// Fallback if path differs
if (!file_exists($config_path)) {
    $config_path = dirname(dirname(dirname(__DIR__))) . '/wp-config.php';
}

if (!file_exists($config_path)) {
    die("❌ wp-config.php not found at: $config_path");
}

$content = file_get_contents($config_path);

// Check if already fixed
if (strpos($content, "YpRd!2024#SecureDB") !== false) {
    die("✅ PASSWORD ALREADY FIXED");
}

// Replace Password
$new_content = str_replace(
    "define( 'DB_PASSWORD', 'SimplePass123' );",
    "define( 'DB_PASSWORD', 'YpRd!2024#SecureDB' );",
    $content
);

if ($content === $new_content) {
    // Maybe different spacing? Try regex or manual check
    die("⚠️ Content didn't change (Search string not exact match?). Check file manually.");
}

// Write back
if (file_put_contents($config_path, $new_content)) {
    echo "✅ SUCCESS: Password updated to YpRd!2024#SecureDB";
} else {
    echo "❌ ERROR: Could not write to wp-config.php (Permissions?)";
}
?>
