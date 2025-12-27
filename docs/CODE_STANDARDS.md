# YourParty.tech - Code Standards & Best Practices

## 📁 Directory Structure Rules

### DO ✅
- Put production Python code in `apps/api/`
- Put WordPress theme files in `apps/web/`
- Put one-off scripts in `scripts/`
- Put dev tools in `tools/`
- Put tests in `tests/`
- Archive old code in `_archive/`

### DON'T ❌
- Put scripts in root directory
- Create multiple entry points (only ONE `api.py` or `main.py`)
- Commit log files, temp files, or backups
- Hardcode IP addresses in code

## 🔧 API Development Rules

### Single Source of Truth
- **Entry Point**: `apps/api/api.py` (App config, Middleware, Route mounting)
- **Routers**: `apps/api/routers/` (Domain-specific endpoints)
- **Models**: `apps/api/models/` (Pydantic schemas)
- **MongoDB Client**: `apps/api/mongo_client.py`

### Endpoint Naming Convention
```
GET /resource          # List all
GET /resource/{id}     # Get one
POST /resource         # Create
PUT /resource/{id}     # Update
DELETE /resource/{id}  # Delete
POST /resource/action  # Special action
```

### Always Include
- Error handling with proper HTTP status codes
- Logging for debug purposes
- CORS headers for frontend access
- JSON response format

## 🌐 WordPress Proxy Rules

### Route Registration
All custom endpoints must be registered in `apps/web/inc/api.php`:
```php
register_rest_route('yourparty/v1', '/endpoint', [...]);
```

### Proxying to FastAPI
- Use `yourparty_api_base_url()` for backend URL
- Include proper error handling
- Return JSON responses

## 📝 Git Commit Rules

### Commit Message Format
```
type: short description

- Detail 1
- Detail 2
```

### Types
- `fix:` Bug fix
- `feat:` New feature
- `refactor:` Code cleanup
- `docs:` Documentation
- `deploy:` Deployment related

### Before Committing
1. Remove debug code
2. No hardcoded credentials
3. No log files or temp data
4. Test changes work

## 🧪 Testing Checklist

Before deploying any change:
- [ ] API endpoint responds correctly (`curl`)
- [ ] No JavaScript console errors
- [ ] No PHP errors in logs
- [ ] Website loads in browser
- [ ] Control panel shows data

## 📚 Documentation Requirements

When adding new features:
1. Add endpoint to `/system-cheatsheet` workflow
2. Update `.gemini_notes.md` if needed
3. Add to CHANGELOG.md
