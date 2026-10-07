$ErrorActionPreference = 'Stop'
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
& $taskPython (Join-Path $taskRoot 'research/calibration_companion.py')
