<?php
echo "Fixing Requests Library...\n";
$zipFile = '/tmp/latest_php.zip';
$extractPath = '/tmp/wp_requests_fix';

if (!file_exists($zipFile) || filesize($zipFile) < 1000000) {
    echo "Downloading core again (fallback)...\n";
    copy('https://wordpress.org/latest.zip', $zipFile);
}

$zip = new ZipArchive;
if ($zip->open($zipFile) === TRUE) {
    if (!$zip->extractTo($extractPath, [
        'wordpress/wp-includes/class-requests.php',
        'wordpress/wp-includes/Requests/src/Autoload.php',
        'wordpress/wp-includes/Requests/src/Requests.php',
        'wordpress/wp-includes/Requests/src/Auth.php',
        'wordpress/wp-includes/Requests/src/Transport.php',
        'wordpress/wp-includes/Requests/src/Transport/Curl.php',
        // Add minimal set? No, extract whole Requests folder logic difficult with extractTo array
        // Better: Extract all, then copy.
    ])) {
        // Fallback: Extract EVERYTHING then copy
        $zip->extractTo($extractPath);
    }
    $zip->close();
    
    // Copy class-requests.php
    $srcClass = "$extractPath/wordpress/wp-includes/class-requests.php";
    $destClass = "/var/www/html/wp-includes/class-requests.php";
    if (copy($srcClass, $destClass)) echo "Replaced class-requests.php\n";
    
    // Copy Requests Directory Recursively (Logic)
    $srcDir = "$extractPath/wordpress/wp-includes/Requests";
    $destDir = "/var/www/html/wp-includes/Requests";
    
    // Delete destination first to be sure
    system("rm -rf $destDir");
    system("cp -r $srcDir $destDir"); // Use CP for directory recursion simplicity in PHP
    echo "Replaced Requests Dir.\n";
    
} else {
    echo "Failed to open ZIP.\n";
}
echo "Done.\n";
?>
