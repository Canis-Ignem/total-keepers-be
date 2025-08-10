# PostgreSQL Database Management Script for Total Keeper (PowerShell)

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "logs", "connect", "reset")]
    [string]$Action
)

switch ($Action) {
    "start" {
        Write-Host "Starting PostgreSQL database..." -ForegroundColor Green
        podman-compose up -d postgres
        Write-Host "PostgreSQL is starting. Use 'podman-compose logs postgres' to check logs." -ForegroundColor Yellow
    }
    "stop" {
        Write-Host "Stopping PostgreSQL database..." -ForegroundColor Yellow
        podman-compose stop postgres
    }
    "restart" {
        Write-Host "Restarting PostgreSQL database..." -ForegroundColor Yellow
        podman-compose restart postgres
    }
    "logs" {
        Write-Host "Showing PostgreSQL logs..." -ForegroundColor Cyan
        podman-compose logs -f postgres
    }
    "connect" {
        Write-Host "Connecting to PostgreSQL..." -ForegroundColor Cyan
        podman-compose exec postgres psql -U postgres -d total_keeper_db
    }
    "reset" {
        Write-Host "⚠️  This will delete all data. Are you sure? (y/N)" -ForegroundColor Red
        $response = Read-Host
        if ($response -match "^[Yy]$") {
            Write-Host "Stopping and removing containers and volumes..." -ForegroundColor Red
            podman-compose down -v
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
