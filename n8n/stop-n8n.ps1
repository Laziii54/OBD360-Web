$connection = Get-NetTCPConnection -LocalPort 5678 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -First 1

if (-not $connection) {
    Write-Host 'n8n is not running.' -ForegroundColor Yellow
    exit 0
}

Stop-Process -Id $connection.OwningProcess -Force
Write-Host 'n8n stopped.' -ForegroundColor Green
