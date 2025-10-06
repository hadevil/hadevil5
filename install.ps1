# Automated installation script for Paradex Market Maker Bot
# Run this in PowerShell: .\install.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Paradex Market Maker Bot - Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found!" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Check Python version
$versionString = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$version = [decimal]$versionString
if ($version -lt 3.8) {
    Write-Host "✗ Python 3.8+ required. You have Python $versionString" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, skipping..." -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host "✓ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q
Write-Host "✓ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create .env from example if it doesn't exist
if (-Not (Test-Path ".env")) {
    Write-Host "Creating .env file from example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "⚠ IMPORTANT: Edit .env and add your API keys!" -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists" -ForegroundColor Gray
}

Write-Host ""

# Generate optimized configurations
Write-Host "Generating optimized configurations..." -ForegroundColor Yellow
python optimize_config.py
Write-Host ""

# Test connection (optional)
Write-Host "Would you like to test the connection now? (y/n)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "Make sure you've added your API keys to config.json first!" -ForegroundColor Yellow
    Write-Host "Press Enter to continue or Ctrl+C to cancel..." -ForegroundColor Yellow
    Read-Host
    
    # Copy conservative config as default
    if (-Not (Test-Path "config.json")) {
        Copy-Item "config_conservative.json" "config.json"
        Write-Host "Using conservative config as default" -ForegroundColor Green
    }
    
    Write-Host ""
    python test_connection.py
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit config.json and add your Paradex API keys" -ForegroundColor White
Write-Host "2. Choose a configuration profile:" -ForegroundColor White
Write-Host "   - Conservative: copy config_conservative.json config.json" -ForegroundColor White
Write-Host "   - Balanced:     copy config_balanced.json config.json" -ForegroundColor White
Write-Host "   - Aggressive:   copy config_aggressive.json config.json" -ForegroundColor White
Write-Host "3. Test connection: python test_connection.py" -ForegroundColor White
Write-Host "4. Run backtest: python backtest.py" -ForegroundColor White
Write-Host "5. Start bot: python paradex_market_maker.py" -ForegroundColor White
Write-Host "6. Monitor: python monitor.py (in another terminal)" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see README.md and QUICK_START.md" -ForegroundColor Cyan
Write-Host ""
