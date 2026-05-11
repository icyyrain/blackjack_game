param(
    [string]$EnvName = "blackjack-build",
    [string]$CondaExe = "C:\miniconda3\Scripts\conda.exe"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$ExePath = Join-Path $ProjectRoot "dist\Blackjack.exe"

if (-not (Test-Path -LiteralPath $CondaExe)) {
    throw "Conda was not found at $CondaExe. Pass -CondaExe with the path to conda.exe."
}

$RunningExe = Get-Process -Name "Blackjack" -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -eq $ExePath }
if ($RunningExe) {
    throw "Close dist\Blackjack.exe before building. It is currently running and Windows will not let PyInstaller replace it."
}

& $CondaExe run -n $EnvName python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name Blackjack `
    --specpath build `
    --paths src `
    src\blackjack\gui.py

Write-Host "Built $ExePath"
