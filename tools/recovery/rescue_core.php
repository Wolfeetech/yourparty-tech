<?php
echo "Starting Rescue...\n";

$url = 'https://wordpress.org/latest.zip';
$zipFile = '/tmp/latest_php.zip';
$extractPath = '/tmp/wp_php_clean';

if (file_exists($extractPath)) {
    echo "Cleaning cleanup dir...\n";
    system("rm -rf $extractPath");
}

echo "Downloading...\n";
$fp = fopen($zipFile, 'w+');
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_TIMEOUT, 300);
curl_setopt($ch, CURLOPT_FILE, $fp);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_exec($ch);
curl_close($ch);
fclose($fp);

if (!file_exists($zipFile) || filesize($zipFile) < 1000000) {
    die("Download failed.\n");
}
echo "Download OK (" . filesize($zipFile) . " bytes).\n";

$zip = new ZipArchive;
if ($zip->open($zipFile) === TRUE) {
    if (!$zip->extractTo($extractPath)) {
        die("Extraction failed.\n");
    }
    $zip->close();
    echo "Extraction OK.\n";
} else {
    die("Failed to open ZIP.\n");
}

echo "Replacing Core Files...\n";
$source = $extractPath . '/wordpress';
$dest = '/var/www/html';

// Move wp-includes
system("rm -rf $dest/wp-includes");
if (rename("$source/wp-includes", "$dest/wp-includes")) {
    echo "wp-includes replaced.\n";
} else {
    echo "wp-includes move failed. Trying cp...\n";
    system("cp -r $source/wp-includes $dest/");
}

// Copy root PHP files
foreach (glob("$source/*.php") as $file) {
    $base = basename($file);
    if ($base === 'wp-config.php') continue; 
    copy($file, "$dest/$base");
    echo "Copied $base\n";
}

system("chown -R www-data:www-data $dest/wp-includes $dest/*.php");
echo "Rescue Complete.\n";
?>
