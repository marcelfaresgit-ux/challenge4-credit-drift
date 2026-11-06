$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
  throw "Execute este arquivo .ps1 como script; nao cole suas linhas no prompt. Use monitoring\run_dashboard.cmd."
}
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
& .\.venv\Scripts\python.exe -m streamlit run monitoring/dashboard.py
