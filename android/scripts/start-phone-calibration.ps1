$ErrorActionPreference = 'Stop'
# Explicit research opt-in. Historical replays can select fixed-time-v2 instead.
if (-not $env:GAITTRACE_DISTANCE_PIPELINE) {
    $env:GAITTRACE_DISTANCE_PIPELINE = 'fixed-time-rows-quiet-v1'
}
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskPython = Join-Path $env:USERPROFILE '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    $taskPython = (Get-Command python -ErrorAction Stop).Source
}
& $taskPython -m pip install 'qrcode[pil]==8.2'
if ($LASTEXITCODE -ne 0) { throw 'Could not prepare the local pairing code.' }
# Reuse an existing compatible OpenCV installation; install only if detection is absent.
& $taskPython -c "import cv2; assert hasattr(cv2.aruco, 'CharucoDetector')"
if ($LASTEXITCODE -ne 0) {
    & $taskPython -m pip install 'opencv-contrib-python-headless==4.12.0.88'
    if ($LASTEXITCODE -ne 0) { throw 'Could not prepare the local framing display.' }
}
Write-Host 'Preparing the experimental scene-calibration model (GPU preferred).'
& $taskPython (Join-Path $taskRoot 'research/rapid_calibration.py') --setup
if ($LASTEXITCODE -ne 0) { Write-Warning 'Scene enrollment could not be prepared. Existing board calibration remains available; inspect the setup output before retrying quick enrollment.' }
& $taskPython (Join-Path $taskRoot 'research/calibration_companion.py')
