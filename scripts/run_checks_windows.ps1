$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
  throw "Execute este arquivo .ps1 como script; nao cole suas linhas no prompt. Use scripts\run_checks_windows.cmd."
}
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$python = ".\.venv\Scripts\python.exe"
$ruff = ".\.venv\Scripts\ruff.exe"
if (-not (Test-Path -LiteralPath $python)) {
  throw "Ambiente nao encontrado. Execute .\scripts\setup_windows.cmd primeiro."
}
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Os testes automatizados falharam." }
& $ruff check .
if ($LASTEXITCODE -ne 0) { throw "O lint encontrou problemas." }
Write-Host "Testes e lint concluidos com sucesso."
