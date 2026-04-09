#!/bin/bash
cat >> /var/www/html/wp-config.php << 'EOF'

/* Security Hardening - Added 2025-12-18 */
define('DISALLOW_FILE_EDIT', true);
define('FORCE_SSL_ADMIN', true);
EOF
grep DISALLOW_FILE_EDIT /var/www/html/wp-config.php && echo "HARDENED"
