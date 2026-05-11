param(
    [string]$EnvName = "blackjack-game",
    [string]$CondaExe = ""
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot
$ExePath = Join-Path $ProjectRoot "dist\Blackjack.exe"

function Resolve-CondaExe {
    param(
        [string]$ExplicitCondaExe
    )

    if ($ExplicitCondaExe) {
        return $ExplicitCondaExe
    }

    $CondaCommand = Get-Command conda.exe -ErrorAction SilentlyContinue
    if ($CondaCommand) {
        return $CondaCommand.Source
    }

    $CandidatePaths = @(
        (Join-Path $env:USERPROFILE "miniconda3\Scripts\conda.exe"),
        (Join-Path $env:USERPROFILE "anaconda3\Scripts\conda.exe"),
        "C:\ProgramData\miniconda3\Scripts\conda.exe",
        "C:\ProgramData\anaconda3\Scripts\conda.exe",
        "C:\miniconda3\Scripts\conda.exe",
        "C:\anaconda3\Scripts\conda.exe"
    )

    foreach ($CandidatePath in $CandidatePaths) {
        if (Test-Path -LiteralPath $CandidatePath) {
            return $CandidatePath
        }
    }

    return $null
}

$CondaExe = Resolve-CondaExe -ExplicitCondaExe $CondaExe
if (-not (Test-Path -LiteralPath $CondaExe)) {
    throw "Conda was not found. Pass -CondaExe with the path to conda.exe, for example: -CondaExe `"$env:USERPROFILE\miniconda3\Scripts\conda.exe`""
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

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE."
}

Write-Host "Built $ExePath"
