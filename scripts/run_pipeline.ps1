param([int]$Rows = 60000)
$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
  throw "Execute este arquivo .ps1 como script; nao cole suas linhas no prompt. Use scripts\run_pipeline.cmd."
}
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
  throw "Ambiente nao encontrado. Execute .\scripts\setup_windows.cmd primeiro."
}
& .\.venv\Scripts\python.exe -m credit_drift.cli run --rows $Rows
if ($LASTEXITCODE -ne 0) { throw "Pipeline falhou; consulte a mensagem acima e logs/pipeline_events.jsonl." }
Write-Host "Relatorios gerados em reports\generated."
