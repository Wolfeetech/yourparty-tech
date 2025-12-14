# Vaultwarden Deployment (Final Hardening)

Ready-to-run setup for the password manager container (intended for LXC VMID 108 on Proxmox or any Docker host).

## 1) Prepare
- Copy `.env.example` to `.env` and set:
  - `VAULTWARDEN_DOMAIN` to your HTTPS URL (e.g. `https://vault.yourparty.tech`)
  - `VAULTWARDEN_ADMIN_TOKEN` to a long random string (store it securely once Vaultwarden is up)
  - SMTP values for invites/2FA backup delivery
- Keep `SIGNUPS_ALLOWED=false` and `INVITATIONS_ALLOWED=false` so only the admin can create users.

## 2) Run
```bash
cd infrastructure/vaultwarden
docker compose pull
docker compose up -d
```
Service listens on `8080` (HTTP). Terminate TLS at Nginx Proxy Manager (VMID 103) or another reverse proxy:
- Hostname: `vault.yourparty.tech`
- Forward to: `http://<vaultwarden-host>:8080`
- Force HTTPS, enable HSTS, and only allow strong ciphers.

## 3) Initial Admin
- Open `https://vault.yourparty.tech/admin` and use the `VAULTWARDEN_ADMIN_TOKEN`.
- Create a single owner account, then turn off admin panel exposure unless needed (`ADMIN_TOKEN` stays configured; just avoid exposing `/admin` in the proxy).
- Disable public signups in the UI (keeps parity with env).

## 4) Backups
```bash
./backup.sh ./backups
```
Creates `tar.gz` snapshots of `./data` and prunes older than 30 days. Place the backups on Proxmox Backup Server (VMID 109) via a cron on the container host, e.g.:
```
0 3 * * * cd /opt/yourparty-tech/infrastructure/vaultwarden && ./backup.sh /var/backups/vaultwarden
```

## 5) Hardening Checklist
- Enforce HTTPS only at the proxy; add Auth on `/admin` path if possible.
- Restrict inbound to proxy+VPN networks via firewall (NPM / host firewall).
- Turn on 2FA for all users; store recovery codes offline.
- Monitor container health: `docker compose ps` and `docker compose logs vaultwarden`.
- Keep image updated: `docker compose pull && docker compose up -d`.

## 6) Next: Secret Migration
Once Vaultwarden is reachable:
1) Create a shared org and collections (prod, staging, infra).
2) Store the rotated secrets (AzuraCast API key, Mongo root pass, SMTP creds, WP salts, etc.) there.
3) Export `.env` files from Vaultwarden to hosts; remove hardcoded defaults from code after migration.
