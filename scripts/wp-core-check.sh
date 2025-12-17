#!/bin/bash
# WordPress Core Integrity Check
# Checks critical files and auto-restores from official WordPress if missing

LOG=/var/log/wp-core-check.log
WP_DIR=/var/www/html
WP_VER=6.7

# Critical files to check
CRITICAL_FILES=(
  "wp-includes/compat.php"
  "wp-includes/version.php"
  "wp-includes/load.php"
  "wp-settings.php"
  "index.php"
)

check_files() {
  for f in "${CRITICAL_FILES[@]}"; do
    if [[ ! -f "$WP_DIR/$f" ]]; then
      echo "$(date): MISSING $f" >> $LOG
      return 1
    fi
  done
  return 0
}

restore_core() {
  echo "$(date): Restoring WordPress $WP_VER core..." >> $LOG
  cd /tmp
  curl -sL -o wp.tar.gz https://wordpress.org/wordpress-$WP_VER.tar.gz
  tar xzf wp.tar.gz
  
  # Restore wp-includes
  rm -rf $WP_DIR/wp-includes
  cp -r wordpress/wp-includes $WP_DIR/
  
  # Restore core files
  cp wordpress/wp-settings.php $WP_DIR/
  cp wordpress/index.php $WP_DIR/
  cp wordpress/wp-load.php $WP_DIR/
  cp wordpress/wp-blog-header.php $WP_DIR/
  
  chown -R www-data:www-data $WP_DIR/wp-includes $WP_DIR/*.php
  rm -rf wordpress wp.tar.gz
  
  echo "$(date): Restore complete" >> $LOG
  systemctl restart apache2
}

# Main
if ! check_files; then
  restore_core
else
  echo "$(date): All core files OK" >> $LOG
fi
