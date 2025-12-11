#!/bin/bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
-keyout /etc/ssl/private/yourparty.self.key \
-out /etc/ssl/certs/yourparty.self.crt \
-subj "/CN=yourparty.tech/O=YourParty Tech" \
-addext "subjectAltName=DNS:yourparty.tech,DNS:*.yourparty.tech,DNS:api.yourparty.tech"
systemctl reload nginx
echo "Cert regenerated and Nginx reloaded."
