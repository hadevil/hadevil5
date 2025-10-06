# PowerShell script to start monitoring dashboard
# Usage: .\start_monitor.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Paradex Market Maker - Monitor" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path "venv") {
    & .\venv\Scripts\Activate.ps1
}

# Start monitor
python monitor.py
