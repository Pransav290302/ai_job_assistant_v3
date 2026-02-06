# Run backend with this project's venv (no requirements.txt needed)
$venvPython = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Error "Venv not found. Create it: python -m venv venv"
    exit 1
}
& $venvPython (Join-Path $PSScriptRoot "main.py")
