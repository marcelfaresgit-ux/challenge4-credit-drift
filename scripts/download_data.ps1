param(
  [string]$Destination = "data/raw"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$target = Join-Path $root $Destination
New-Item -ItemType Directory -Force -Path $target | Out-Null

$kaggle = Join-Path $root ".venv\Scripts\kaggle.exe"
if (-not (Test-Path -LiteralPath $kaggle)) {
  throw "Kaggle CLI nao encontrado. Execute .\scripts\setup_windows.ps1 primeiro."
}

Write-Host "Baixando application_train.csv da competicao oficial Home Credit Default Risk..."
Write-Host "O download requer conta Kaggle e aceite previo das regras da competicao."
& $kaggle competitions download -c home-credit-default-risk -f application_train.csv -p $target --force
if ($LASTEXITCODE -ne 0) {
  throw "Download nao concluido. Confira o login Kaggle, aceite das regras e veja docs/DATASET.md."
}

$zip = Join-Path $target "application_train.csv.zip"
if (Test-Path -LiteralPath $zip) {
  Expand-Archive -LiteralPath $zip -DestinationPath $target -Force
  Remove-Item -LiteralPath $zip
}
if (-not (Test-Path -LiteralPath (Join-Path $target "application_train.csv"))) {
  throw "O arquivo esperado application_train.csv nao foi encontrado em $target."
}
Write-Host "Dataset pronto em $target\application_train.csv"
