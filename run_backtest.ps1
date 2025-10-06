# Run backtesting scenarios
# Usage: .\run_backtest.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Paradex Market Maker - Backtest" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path "venv") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "✓ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run .\install.ps1 first" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Running backtesting scenarios..." -ForegroundColor Yellow
Write-Host "This will simulate 24 hours of trading with different configurations" -ForegroundColor Gray
Write-Host ""

# Run backtest
python backtest.py

Write-Host ""
Write-Host "Backtest complete!" -ForegroundColor Green
Write-Host "Results saved to backtest_results.json" -ForegroundColor Cyan
Write-Host ""
