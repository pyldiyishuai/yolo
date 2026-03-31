# Windows one-click start script for Visual Assist System
# Usage: powershell -ExecutionPolicy Bypass -File deploy\start.ps1

$ErrorActionPreference = "Stop"
$ROOT     = Split-Path -Parent $PSScriptRoot
$BACKEND  = Join-Path $ROOT "backend"
$FRONTEND = Join-Path $ROOT "frontend"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  Visual Assist System - Start"     -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python not found. Please install Python 3.10+" -ForegroundColor Red
    pause; exit 1
}

# Install backend deps
Write-Host "`n[1/3] Installing backend dependencies..." -ForegroundColor Yellow
python -m pip install -r "$BACKEND\requirements.txt"
Write-Host "  Done." -ForegroundColor Green

# Start backend
Write-Host "[2/3] Starting backend (http://127.0.0.1:8000)..." -ForegroundColor Yellow
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "python"
$psi.Arguments = "-m uvicorn main:app --host 127.0.0.1 --port 8000"
$psi.WorkingDirectory = $BACKEND
$psi.UseShellExecute = $true
$psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Minimized
$backendProc = [System.Diagnostics.Process]::Start($psi)
Write-Host "  Backend PID: $($backendProc.Id)" -ForegroundColor Gray
Start-Sleep -Seconds 3

# Start frontend
Write-Host "[3/3] Starting frontend dev server..." -ForegroundColor Yellow
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmCmd) {
    Write-Host "[WARN] npm not found. Run manually: cd frontend && npm install && npm run dev" -ForegroundColor Yellow
} else {
    if (-not (Test-Path "$FRONTEND\node_modules")) {
        Write-Host "  Installing frontend dependencies (first time)..." -ForegroundColor Gray
        $npmPath = $npmCmd.Source
        $installPsi = New-Object System.Diagnostics.ProcessStartInfo
        $installPsi.FileName = $npmPath
        $installPsi.Arguments = "install"
        $installPsi.WorkingDirectory = $FRONTEND
        $installPsi.UseShellExecute = $false
        $installPsi.RedirectStandardOutput = $false
        $installProc = [System.Diagnostics.Process]::Start($installPsi)
        $installProc.WaitForExit()
    }
    $npmPath = $npmCmd.Source
    $frontPsi = New-Object System.Diagnostics.ProcessStartInfo
    $frontPsi.FileName = $npmPath
    $frontPsi.Arguments = "run dev"
    $frontPsi.WorkingDirectory = $FRONTEND
    $frontPsi.UseShellExecute = $true
    $frontPsi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Normal
    $frontendProc = [System.Diagnostics.Process]::Start($frontPsi)
    Write-Host "  Frontend PID: $($frontendProc.Id)" -ForegroundColor Gray
    Start-Sleep -Seconds 4
    Start-Process "http://localhost:5173"
}

Write-Host ""
Write-Host "System started!" -ForegroundColor Green
Write-Host "  Frontend : http://localhost:5173"     -ForegroundColor White
Write-Host "  Backend  : http://127.0.0.1:8000"     -ForegroundColor White
Write-Host "  API Docs : http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit (services keep running)..." -ForegroundColor Gray
pause
