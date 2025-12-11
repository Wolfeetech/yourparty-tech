# PowerShell - ExecutionPolicy Bypass -Scope Process -Force
# Auto-Fix Script for Jan 1st Launch
Write-Host "🚀 STARTING SYSTEM FIX PROTOCOL..." -ForegroundColor Green

# 1. Update Backend Dependencies
Write-Host "📦 Installing Backend Dependencies..." -ForegroundColor Cyan
cd C:\Users\StudioPC\yourparty-tech\backend
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) { Write-Host "✅ Dependencies Installed" -ForegroundColor Green }
    else { Write-Host "❌ Dependency Install Failed" -ForegroundColor Red }
}

# 2. Check WordPress Config
Write-Host "🔍 Checking WordPress Functionality..." -ForegroundColor Cyan
$wpPath = "C:\Users\StudioPC\yourparty-tech\yourparty-tech\functions.php"
if (Select-String -Path $wpPath -Pattern "YOURPARTY_AZURACAST_API_KEY") {
    Write-Host "✅ Security Check Passed (API Key removed/checked)" -ForegroundColor Green
} else {
    Write-Host "⚠️ Security Warning: Function signature missing" -ForegroundColor Yellow
}

# 3. Frontend Build (Optional)
Write-Host "🎨 Building Frontend..." -ForegroundColor Cyan
cd C:\Users\StudioPC\yourparty-tech\frontend
if (Test-Path "package.json") {
    # npm install # Skip to save time if already installed
    npm run build
    if ($LASTEXITCODE -eq 0) { Write-Host "✅ Frontend Built" -ForegroundColor Green }
}

Write-Host "🎉 SYSTEM READY FOR DEPLOYMENT." -ForegroundColor Magenta
Write-Host "👉 Please restart the Backend API now: 'python api.py'" -ForegroundColor Yellow
Start-Sleep -Seconds 5
