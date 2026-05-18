#!/bin/bash
/sbin/mariadbd --user=root --console > /tmp/db_diag.log 2>&1
cat /tmp/db_diag.log
