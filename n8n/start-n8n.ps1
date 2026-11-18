$ErrorActionPreference = 'Stop'

$env:N8N_PORT = '5678'
$env:N8N_HOST = 'localhost'
$env:N8N_PROTOCOL = 'http'
$env:N8N_SECURE_COOKIE = 'false'
$env:N8N_BLOCK_ENV_ACCESS_IN_NODE = 'false'
$env:N8N_DIAGNOSTICS_ENABLED = 'false'
$env:N8N_TELEMETRY_ENABLED = 'false'

# Optional: Telegram alerts for the critical DTC workflow.
# Uncomment and set your bot token and chat id before starting n8n.
# $env:OBD360_TELEGRAM_BOT_TOKEN = '123456:ABC...'
# $env:OBD360_TELEGRAM_CHAT_ID = '123456789'

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host 'Node.js is not installed. Install Node.js 24 or newer.' -ForegroundColor Red
    exit 1
}

$npmRoot = (npm root -g).Trim()
$n8nBin = Join-Path $npmRoot 'n8n\bin\n8n'

if (-not (Test-Path $n8nBin)) {
    Write-Host 'n8n is not installed. Run: npm install -g n8n@2.47.4' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host '  OBD360 n8n' -ForegroundColor Green
Write-Host '  http://localhost:5678' -ForegroundColor Cyan
Write-Host '  Press Ctrl+C to stop' -ForegroundColor DarkGray
Write-Host ''

& node $n8nBin start
