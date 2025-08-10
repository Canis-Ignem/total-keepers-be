# PostgreSQL Database Management Script - Universal (Docker/Podman)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "logs", "connect", "reset")]
    [string]$Action
)

# Detect if using Docker or Podman
$ComposeCmd = "docker-compose"
if (Get-Command "podman-compose" -ErrorAction SilentlyContinue) {
    $ComposeCmd = "podman-compose"
    Write-Host "Using Podman Compose" -ForegroundColor Cyan
} elseif (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
    $ComposeCmd = "docker-compose"
    Write-Host "Using Docker Compose" -ForegroundColor Cyan
} else {
    Write-Host "❌ Neither docker-compose nor podman-compose found!" -ForegroundColor Red
    Write-Host "Please install Docker or Podman first." -ForegroundColor Yellow
    exit 1
}

switch ($Action) {
    "start" {
        Write-Host "Starting PostgreSQL database..." -ForegroundColor Green
        & $ComposeCmd up -d postgres
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ PostgreSQL started successfully!" -ForegroundColor Green
            Write-Host "Use '.\db.ps1 logs' to check logs or '.\db.ps1 connect' to connect." -ForegroundColor Yellow
        } else {
            Write-Host "❌ Failed to start PostgreSQL. Check logs with '.\db.ps1 logs'" -ForegroundColor Red
        }
    }
    "stop" {
        Write-Host "Stopping PostgreSQL database..." -ForegroundColor Yellow
        & $ComposeCmd stop postgres
    }
    "restart" {
        Write-Host "Restarting PostgreSQL database..." -ForegroundColor Yellow
        & $ComposeCmd restart postgres
    }
    "logs" {
        Write-Host "Showing PostgreSQL logs..." -ForegroundColor Cyan
        & $ComposeCmd logs -f postgres
    }
    "connect" {
        Write-Host "Connecting to PostgreSQL..." -ForegroundColor Cyan
        & $ComposeCmd exec postgres psql -U postgres -d total_keeper_db
    }
    "reset" {
        Write-Host "⚠️  This will delete all data. Are you sure? (y/N)" -ForegroundColor Red
        $response = Read-Host
        if ($response -match "^[Yy]$") {
            Write-Host "Stopping and removing containers and volumes..." -ForegroundColor Red
            & $ComposeCmd down -v
            Write-Host "Database reset complete. Run '.\db.ps1 start' to start fresh." -ForegroundColor Green
        } else {
            Write-Host "Reset cancelled." -ForegroundColor Yellow
        }
    }
}

# Usage information
if ($Action -eq $null) {
    Write-Host "Usage: .\db.ps1 {start|stop|restart|logs|connect|reset}" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor White
    Write-Host "  start   - Start the PostgreSQL container" -ForegroundColor Gray
    Write-Host "  stop    - Stop the PostgreSQL container" -ForegroundColor Gray
    Write-Host "  restart - Restart the PostgreSQL container" -ForegroundColor Gray
    Write-Host "  logs    - Show and follow PostgreSQL logs" -ForegroundColor Gray
    Write-Host "  connect - Connect to PostgreSQL CLI" -ForegroundColor Gray
    Write-Host "  reset   - Remove all data and containers (DESTRUCTIVE)" -ForegroundColor Gray
}
