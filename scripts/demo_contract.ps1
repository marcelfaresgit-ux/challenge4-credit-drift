$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
  throw "Execute este arquivo .ps1 como script; nao cole suas linhas no prompt. Use scripts\demo_contract.cmd."
}
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& .\.venv\Scripts\python.exe -m credit_drift.cli demo-contract
