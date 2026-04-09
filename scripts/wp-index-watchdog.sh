#!/bin/bash
# WordPress Index.php Watchdog
# Checks for malware patterns and restores if infected

INDEX=/var/www/html/index.php
LOG=/var/log/wp-index-watchdog.log
CLEAN_MD5="b6a17a8c4bb62ce1656b3c0cfd0c6d13"  # WordPress 6.7 index.php md5

# Check if index.php contains malware patterns
if grep -q 'goto [A-Za-z0-9]*;' "$INDEX" 2>/dev/null || \
   grep -q 'eval(base64' "$INDEX" 2>/dev/null || \
   grep -q 'CURLOPT' "$INDEX" 2>/dev/null; then
  echo "$(date): MALWARE DETECTED in index.php - restoring" >> $LOG
  
  # Download clean index.php
  curl -sL -o "$INDEX" https://raw.githubusercontent.com/WordPress/WordPress/6.7/index.php
  
  echo "$(date): index.php restored" >> $LOG
fi
