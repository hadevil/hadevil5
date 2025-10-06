# PowerShell script to start Paradex Market Maker Bot
# Usage: .\start_bot.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Paradex Market Maker Bot" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& .\venv\Scripts\Activate.ps1

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Green
pip install -q -r requirements.txt

# Check if config exists
if (-Not (Test-Path "config.json")) {
    Write-Host "ERROR: config.json not found!" -ForegroundColor Red
    Write-Host "Please create config.json from config.json.example" -ForegroundColor Yellow
    exit 1
}

# Check if .env exists
if (-Not (Test-Path ".env")) {
    Write-Host "WARNING: .env not found!" -ForegroundColor Yellow
    Write-Host "API keys will be loaded from config.json" -ForegroundColor Yellow
}

# Display configuration
Write-Host ""
Write-Host "Configuration loaded successfully" -ForegroundColor Green
Write-Host "Starting bot..." -ForegroundColor Green
Write-Host ""

# Start the bot
python paradex_market_maker.py

# Keep window open on error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Bot stopped with error code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
