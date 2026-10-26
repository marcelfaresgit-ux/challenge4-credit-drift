$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$pyLauncher = Get-Command py -ErrorAction SilentlyContinue
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pyLauncher) {
  $pythonExe = $pyLauncher.Source
  $pythonPrefix = @("-3.12")
} elseif ($pythonCommand) {
  $pythonExe = $pythonCommand.Source
  $pythonPrefix = @()
} else {
  throw "Python nao encontrado. Instale Python 3.11 ou 3.12 e o launcher py do Windows."
}
& $pythonExe @pythonPrefix -c "import sys; raise SystemExit(0 if (3,11) <= sys.version_info[:2] < (3,13) else 1)"
if ($LASTEXITCODE -ne 0) { throw "Este projeto requer Python 3.11 ou 3.12. Instale com py install 3.12." }

if (-not (Test-Path -LiteralPath ".venv\Scripts\python.exe")) {
  & $pythonExe @pythonPrefix -m venv .venv
}
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[dev,dashboard,kaggle]"
Write-Host "Ambiente pronto. Proximo passo: .\scripts\download_data.ps1"
