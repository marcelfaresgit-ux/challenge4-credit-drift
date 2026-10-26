param([int]$Rows = 60000)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
  throw "Ambiente nao encontrado. Execute .\scripts\setup_windows.ps1 primeiro."
}
& .\.venv\Scripts\python.exe -m credit_drift.cli run --rows $Rows
if ($LASTEXITCODE -ne 0) { throw "Pipeline falhou; consulte a mensagem acima e logs/pipeline_events.jsonl." }
Write-Host "Relatorios gerados em reports\generated."
