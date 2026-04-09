$ErrorActionPreference = "Stop"

# Load Configuration
$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
. "$ScriptDir\config.ps1"

Write-Host "=== YourParty System Health Check ===" -ForegroundColor Cyan
$overall_success = $true

function Run-Test {
    param($Name, $Command)
    Write-Host "`n[$Name]" -ForegroundColor Yellow
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  FAILED (Exit Code: $LASTEXITCODE)" -ForegroundColor Red
            return $false
        }
        else {
            Write-Host "  PASSED" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "  ERROR: $_" -ForegroundColor Red
        return $false
    }
}

# 1. API Responsiveness
$res = Run-Test -Name "API Health (Curl Docs)" -Command "curl -sI http://localhost:8000/docs"
if (-not $res) { $overall_success = $false }

# 2. Interactivity Verification (Ratings/Moods)
$res = Run-Test -Name "Interactive Features (Vote/Tag)" -Command "python tests/verify_interactivity.py"
if (-not $res) { $overall_success = $false }

# 3. Shoutout Verification
$res = Run-Test -Name "Shoutout System" -Command "python tests/verify_shoutouts.py"
if (-not $res) { $overall_success = $false }

Write-Host "`n-------------------------------------"
if ($overall_success) {
    Write-Host "✅ SYSTEM HEALTHY" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "❌ SYSTEM UNHEALTHY" -ForegroundColor Red
    exit 1
}
