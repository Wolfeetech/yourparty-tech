# Security Audit Report: yourparty.tech
**Date**: 2025-12-11  
**Auditor**: Antigravity Agent  
**Scope**: Repository, Backend API, WordPress Theme

---

## Executive Summary

| Category | Status | Critical Issues |
|----------|--------|-----------------|
| Credential Management | ⚠️ Needs Attention | 1 hardcoded key in code |
| Input Validation | ✅ Good | Proper sanitization in place |
| Rate Limiting | ✅ Good | 10 requests/minute per IP |
| Access Control | ✅ Good | Admin endpoints protected |
| CORS Configuration | ✅ Good | Whitelist-based |

---

## 1. Credential Management

### ✅ VERIFIED: `.gitignore` Excludes `.env`

The `.gitignore` file contains `*.env`, preventing environment files from being committed.

### ⚠️ FIXED: Hardcoded API Key in `sync_moods.py`

**Location**: `backend/sync_moods.py` line 15  
**Issue**: AzuraCast API key used as default fallback value  
**Risk**: Medium - Could expose key if code is shared  
**Resolution**: Removed default value, now requires explicit ENV variable

```diff
- AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY", "9199dc63da623190:...")
+ AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY")
+ if not AZURACAST_API_KEY:
+     raise ValueError("AZURACAST_API_KEY environment variable required")
```

### ✅ VERIFIED: Backend `.env` File

Location: `backend/.env`  
- Contains MongoDB and AzuraCast credentials
- Protected by `.gitignore`
- **Recommendation**: Rotate credentials if ever exposed

---

## 2. Backend API Security

### ✅ Input Validation

| Endpoint | Sanitization | Status |
|----------|--------------|--------|
| `/rate` | `preg_replace`, `sanitize_text_field` | ✅ |
| `/mood-tag` | `preg_replace`, `sanitize_text_field` | ✅ |
| `/vote-next` | `sanitize_text_field` | ✅ |

### ✅ Rate Limiting

- **Implementation**: Transient-based per IP
- **Limit**: 10 requests per minute per IP
- **Location**: `api.php` lines 422-438

### ✅ Access Control

Admin-only endpoints properly protected:
- `/control/skip` - `current_user_can('manage_options')`
- `/control/ratings` - `current_user_can('manage_options')`

### ⚠️ Missing: Authentication for Public Endpoints

Public endpoints (`/rate`, `/mood-tag`) use no user authentication.  
**Recommendation**: Add optional token-based auth for registered users.

---

## 3. CORS Configuration

**Location**: `backend/api.py` lines 34-47

Allowed origins (whitelist):
- `https://yourparty.tech`
- `https://www.yourparty.tech`
- `https://radio.yourparty.tech`
- `https://control.yourparty.tech`
- `http://localhost:3000` (dev only)

**Status**: ✅ Properly configured

---

## 4. WordPress Security

### ✅ API Proxy Pattern

WordPress acts as proxy to FastAPI backend, preventing direct backend exposure.

### ⚠️ Internal IPs in Code

**Locations**:
- `api.php:19` - `192.168.178.210` (AzuraCast)
- `api.php:556` - `192.168.178.25` (PVE Host)

**Risk**: Low - Only affects internal routing  
**Recommendation**: Move to `wp-config.php` constants

---

## 5. Recommendations

### Immediate Actions
1. ✅ Remove hardcoded API key from `sync_moods.py`
2. ⚠️ Rotate MongoDB password if concerned about exposure
3. ⚠️ Rotate AzuraCast API key

### Hardening (Optional)
1. Add Security Headers (X-Frame-Options, CSP)
2. Implement CSRF tokens for form submissions
3. Add request signing for API calls
4. Set up automated backup strategy

### Monitoring
1. Enable access logging for `/rate` and `/mood-tag`
2. Set up alerts for rate limit triggers
3. Monitor MongoDB for unusual activity

---

## 6. Server-Side Checks (Manual)

> **Note**: SSH access not available during this audit. Please verify:

```bash
# 1. Check running containers
docker ps

# 2. Verify AzuraCast version
docker exec azuracast cat /var/azuracast/version

# 3. Check exposed ports
netstat -tlnp

# 4. Verify MongoDB authentication
mongo --eval "db.adminCommand('ismaster')"

# 5. Check firewall rules
ufw status
```

---

## Appendix: Files Reviewed

| File | Purpose | Issues Found |
|------|---------|--------------|
| `backend/.env` | Environment variables | Protected by .gitignore |
| `backend/api.py` | Main API | None |
| `backend/sync_moods.py` | Mood sync | Hardcoded key (FIXED) |
| `backend/mongo_client.py` | Database client | None |
| `yourparty-tech/inc/api.php` | WP API proxy | Internal IPs |
| `.gitignore` | Git exclusions | Adequate |

---

*Report generated: 2025-12-11T20:05:00+01:00*
