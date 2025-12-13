<?php
echo "Restoring Full Requests Library...\n";
$zipFile = '/tmp/latest_php.zip';
$extractPath = '/tmp/wp_full_requests';

if (!file_exists($zipFile) || filesize($zipFile) < 1000000) {
    echo "Downloading core...\n";
    copy('https://wordpress.org/latest.zip', $zipFile);
}

$zip = new ZipArchive;
if ($zip->open($zipFile) === TRUE) {
    echo "Zip opened.\n";
    if (!is_dir($extractPath)) {
        mkdir($extractPath, 0755, true);
    }

    $filesToExtract = [];
    for ($i = 0; $i < $zip->numFiles; $i++) {
        $filename = $zip->getNameIndex($i);
        // Match everything in wp-includes/Requests
        if (strpos($filename, 'wordpress/wp-includes/Requests/') === 0) {
            $filesToExtract[] = $filename;
        }
        // Also ensure class-requests.php is there
        if ($filename === 'wordpress/wp-includes/class-requests.php') {
            $filesToExtract[] = $filename;
        }
    }

    echo "Found " . count($filesToExtract) . " files to extract.\n";
    $zip->extractTo($extractPath, $filesToExtract);
    $zip->close();
    
    // Deploy
    $srcDir = "$extractPath/wordpress/wp-includes/Requests";
    $destDir = "/var/www/html/wp-includes/Requests";
    
    echo "Replacing $destDir...\n";
    system("rm -rf $destDir");
    system("cp -r $srcDir $destDir");
    
    // Deploy class-requests.php (using the one from WP core, or keep my alias one? 
    // Core one is a wrapper in 6.7 too. Let's use the Core one first to be safe, or if that fails, revisit my alias wrapper. 
    // Actually, WP 6.7 class-requests.php IS the wrapper.
    // So extracting it from the zip is correct.
    $srcClass = "$extractPath/wordpress/wp-includes/class-requests.php";
    $destClass = "/var/www/html/wp-includes/class-requests.php";
    system("cp $srcClass $destClass");
    echo "Replaced class-requests.php\n";

} else {
    echo "Failed to open ZIP.\n";
}
echo "Done.\n";
?>
