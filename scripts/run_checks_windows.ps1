$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$python = ".\.venv\Scripts\python.exe"
$ruff = ".\.venv\Scripts\ruff.exe"
if (-not (Test-Path -LiteralPath $python)) {
  throw "Ambiente nao encontrado. Execute .\scripts\setup_windows.ps1 primeiro."
}
& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Os testes automatizados falharam." }
& $ruff check .
if ($LASTEXITCODE -ne 0) { throw "O lint encontrou problemas." }
Write-Host "Testes e lint concluidos com sucesso."
