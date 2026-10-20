param(
  [ValidateSet('Setup','Start','Status','Test','PermissionTest','Stop','Sensors')][string]$Action='Start',
  [string]$Apk='', [string]$Package='com.gaitsteps.app', [switch]$ShowWindow,
  [switch]$ResetVirtualApp
)
$ErrorActionPreference='Stop'
$workspace=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$localTools=Join-Path $workspace 'android/dist/mobile-test-tools'
$sdk=Join-Path $workspace 'android/dist/native-distance-tools/android-sdk'
$jdk=Join-Path $workspace 'android/dist/native-distance-tools/jdk-17.0.20.1+1'
$labOutput=Join-Path $workspace 'android/dist/emulator-lab'
$env:ANDROID_HOME=$sdk
$env:ANDROID_SDK_ROOT=$sdk
$env:JAVA_HOME=$jdk
$env:APPIUM_HOME=Join-Path $localTools 'appium-home'
$env:ANDROID_AVD_HOME=Join-Path $localTools 'avd'
$env:PATH="$jdk/bin;$sdk/platform-tools;$sdk/emulator;$env:PATH"
$adb=Join-Path $sdk 'platform-tools/adb.exe'
$emulator=Join-Path $sdk 'emulator/emulator.exe'
$appium=Join-Path $localTools 'node_modules/appium/build/lib/main.js'
$serial='emulator-5560'
$avd='Workspace_API30'
New-Item -ItemType Directory -Force -Path $labOutput,$env:ANDROID_AVD_HOME | Out-Null
function Invoke-Adb([string[]]$Arguments) {
  $answer=& $adb -s $serial @Arguments 2>&1
  if($LASTEXITCODE -ne 0){throw "Emulator ADB failed: $answer"}
  return $answer
}
if($Action -eq 'Setup') {
  $imagePackage=if(Test-Path -LiteralPath (Join-Path $sdk 'cmdline-tools/latest/bin/android.exe')){'system-images/android-30/google_apis/x86_64'}else{'system-images;android-30;google_apis;x86_64'}
  & (Join-Path $sdk 'cmdline-tools/latest/bin/sdkmanager.bat') 'emulator' $imagePackage
  if($LASTEXITCODE -ne 0){throw 'Android SDK download failed.'}
  if(!(Test-Path -LiteralPath $emulator) -or !(Test-Path -LiteralPath (Join-Path $sdk 'system-images/android-30/google_apis/x86_64/system.img'))){throw 'SDK command returned without installing the required emulator/image.'}
  & npm.cmd install --prefix $localTools appium@3.8.0 --no-audit --no-fund
  if($LASTEXITCODE -ne 0){throw 'Appium install failed.'}
  $driverPackage=Join-Path $env:APPIUM_HOME 'node_modules/appium-uiautomator2-driver/package.json'
  if(!(Test-Path -LiteralPath $driverPackage)){
    & node $appium driver install uiautomator2@8.7.0
    if($LASTEXITCODE -ne 0){throw 'Appium driver setup failed.'}
  }
  Write-Host 'Tools ready. Run this script with -Action Start.'
  exit
}
if($Action -eq 'Start') {
  if(!(Test-Path -LiteralPath $emulator) -or !(Test-Path -LiteralPath $appium)){throw 'Run -Action Setup first.'}
  if(!(Test-Path -LiteralPath (Join-Path $env:ANDROID_AVD_HOME "$avd.ini"))){
    'no' | & (Join-Path $sdk 'cmdline-tools/latest/bin/avdmanager.bat') create avd --name $avd --package 'system-images;android-30;google_apis;x86_64' --device pixel_5
    if($LASTEXITCODE -ne 0){throw 'Virtual device creation failed.'}
    $config=Join-Path $env:ANDROID_AVD_HOME "$avd.avd/config.ini"
    Add-Content -LiteralPath $config -Value "`nhw.ramSize=4096`nhw.camera.front=emulated`nhw.camera.back=emulated`nhw.gyroscope=yes`nhw.sensors.magnetic_field=yes"
  }
  $connected=& $adb devices
  if(!($connected -match "$serial\s+(device|offline)")){
    & (Join-Path $sdk 'emulator/emulator-check.exe') accel
    if($LASTEXITCODE -ne 0){throw 'Emulator hardware acceleration unavailable; inspect -accel-check before changing Windows features.'}
    $args=@('-avd',$avd,'-port','5560','-no-snapshot','-no-boot-anim','-gpu','swiftshader','-camera-front','emulated','-camera-back','emulated')
    if(!$ShowWindow){$args+='-no-window'}
    $windowStyle=if($ShowWindow){'Normal'}else{'Hidden'}
    Start-Process -FilePath $emulator -ArgumentList $args -WindowStyle $windowStyle -RedirectStandardOutput (Join-Path $labOutput 'emulator.log') -RedirectStandardError (Join-Path $labOutput 'emulator.stderr.log') | Out-Null
  }
  $deadline=(Get-Date).AddMinutes(3)
  do {
    Start-Sleep -Seconds 2
    try {$boot=& $adb -s $serial shell getprop sys.boot_completed 2>&1} catch {$boot=''}
    if((Get-Date) -gt $deadline){throw "Emulator boot timeout; inspect $labOutput."}
  } until($boot -match '^1$')
  Invoke-Adb @('shell','input','keyevent','82') | Out-Null
  Invoke-Adb @('shell','settings','put','global','window_animation_scale','0') | Out-Null
  Invoke-Adb @('shell','settings','put','global','transition_animation_scale','0') | Out-Null
  Invoke-Adb @('shell','settings','put','global','animator_duration_scale','0') | Out-Null
  try {$ready=Invoke-RestMethod 'http://127.0.0.1:4725/status' -TimeoutSec 2} catch {$ready=$null}
  if(!$ready){
    # ArgumentList needs quoting for paths containing spaces; all values are local constants.
    Start-Process -FilePath (Get-Command node).Source -ArgumentList @(('"'+$appium+'"'),'--address','127.0.0.1','--port','4725','--log-no-colors') -WindowStyle Hidden -RedirectStandardOutput (Join-Path $labOutput 'appium.log') -RedirectStandardError (Join-Path $labOutput 'appium.stderr.log') | Out-Null
    $deadline=(Get-Date).AddSeconds(30)
    do {Start-Sleep -Seconds 1;try {$ready=Invoke-RestMethod 'http://127.0.0.1:4725/status' -TimeoutSec 2}catch{$ready=$null}} until($ready -or (Get-Date) -gt $deadline)
    if(!$ready){throw 'Appium startup failed; inspect appium logs.'}
  }
  Write-Host "Android lab ready: $serial; Appium http://127.0.0.1:4725. Physical phones are never selected."
}
elseif($Action -eq 'Status') {
  & $adb -s $serial get-state
  & $adb -s $serial shell getprop ro.product.cpu.abilist
  Invoke-RestMethod 'http://127.0.0.1:4725/status' | ConvertTo-Json -Depth 5
}
elseif($Action -eq 'Sensors') {
  Invoke-Adb @('emu','sensor','status')
}
elseif($Action -eq 'Test') {
  if(!$Apk){$Apk=Join-Path $labOutput 'GaitTrace-emulator-x86_64.apk'}
  if(!(Test-Path -LiteralPath $Apk)){throw 'Pass -Apk with a built APK path.'}
  & node (Join-Path $PSScriptRoot 'smoke.cjs') --apk (Resolve-Path -LiteralPath $Apk).Path --package $Package
  exit $LASTEXITCODE
}
elseif($Action -eq 'Stop') {
  Invoke-Adb @('emu','kill') | Out-Null
  Write-Host 'Only the dedicated emulator was stopped. Appium is still available for reuse.'
}
elseif($Action -eq 'PermissionTest') {
  if(!$ResetVirtualApp){throw 'Pass -ResetVirtualApp to explicitly discard only the disposable GaitTrace emulator installation for a fresh permission fixture.'}
  if($Package -ne 'com.gaitsteps.app'){throw 'This permission scenario is specific to GaitTrace.'}
  if(!$Apk){$Apk=Join-Path $labOutput 'GaitTrace-emulator-x86_64.apk'}
  if(!(Test-Path -LiteralPath $Apk)){throw 'Build the emulator APK first.'}
  # Repeated denials persist in Android 11; reinstall this disposable virtual app.
  # No physical device or other application is touched.
  Invoke-Adb @('uninstall',$Package) | Out-Null
  Invoke-Adb @('install',(Resolve-Path -LiteralPath $Apk).Path) | Out-Null
  & node (Join-Path $PSScriptRoot 'interact.cjs') --scenario (Join-Path $PSScriptRoot 'scenarios/camera-permission.json')
  exit $LASTEXITCODE
}
