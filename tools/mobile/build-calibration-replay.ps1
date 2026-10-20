# Separate emulator-only test APK. No test transport is added to the patient app.
$ErrorActionPreference='Stop'
$workspace=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$sdk=Join-Path $workspace 'android/dist/native-distance-tools/android-sdk'
$jdk=Join-Path $workspace 'android/dist/native-distance-tools/jdk-17.0.20.1+1'
$env:JAVA_HOME=$jdk
$build=Join-Path $sdk 'build-tools/35.0.0'
$jar=Join-Path $sdk 'platforms/android-35/android.jar'
$output=Join-Path $workspace 'android/dist/emulator-lab/calibration-replay'
$native=Join-Path $workspace 'android/modules/gait-camera-calibration/android/src/main/java/expo/modules/gaitcalibration'
$apk=Join-Path $workspace 'android/dist/emulator-lab/GaitTrace-emulator-x86_64.apk'
New-Item -ItemType Directory -Force -Path $output,(Join-Path $output 'classes'),(Join-Path $output 'dex') | Out-Null
$manifest=@'
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.gaittrace.calibrationlab">
 <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="30"/>
 <application android:label="Calibration numerical lab" android:debuggable="true" android:extractNativeLibs="true"/>
 <instrumentation android:name="expo.modules.gaitcalibration.CalibrationReplayInstrumentation" android:targetPackage="com.gaittrace.calibrationlab"/>
</manifest>
'@
$manifestPath=Join-Path $output 'AndroidManifest.xml'
[IO.File]::WriteAllText($manifestPath,$manifest,[Text.UTF8Encoding]::new($false))
$sources=@('OnDeviceVio','OnDeviceProfile','ReferenceTrackingProfile','VioBootstrap','LiveDistanceGate','SetupConvergenceGate','SetupBaselineGate','GuidedCaptureClock') | ForEach-Object {Join-Path $native "${_}.java"}
$sources+=Join-Path $PSScriptRoot 'CalibrationReplayInstrumentation.java'
& (Join-Path $jdk 'bin/javac.exe') -encoding UTF-8 -source 8 -target 8 -cp $jar -d (Join-Path $output 'classes') @sources
if($LASTEXITCODE -ne 0){throw 'Numerical lab Java compilation failed'}
$classFiles=Get-ChildItem -LiteralPath (Join-Path $output 'classes') -Recurse -Filter '*.class' | ForEach-Object FullName
& (Join-Path $build 'd8.bat') --lib $jar --min-api 26 --output (Join-Path $output 'dex') @classFiles
if($LASTEXITCODE -ne 0){throw 'Numerical lab dex compilation failed'}
$unsigned=Join-Path $output 'lab-unsigned.apk'
& (Join-Path $build 'aapt2.exe') link -I $jar --manifest $manifestPath -o $unsigned
if($LASTEXITCODE -ne 0){throw 'Numerical lab APK linking failed'}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$original=[IO.Compression.ZipFile]::OpenRead($apk)
$target=[IO.Compression.ZipFile]::Open($unsigned,[IO.Compression.ZipArchiveMode]::Update)
try {
 [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($target,(Join-Path $output 'dex/classes.dex'),'classes.dex') | Out-Null
 foreach($name in @('libgait_openvins.so','libopencv_java4.so','libc++_shared.so')){
  $entry=$original.GetEntry("lib/x86_64/$name")
  if(!$entry){throw "Missing production library $name"}
  $copy=$target.CreateEntry("lib/x86_64/$name")
  $inputStream=$entry.Open();$outputStream=$copy.Open()
  try{$inputStream.CopyTo($outputStream)}finally{$inputStream.Dispose();$outputStream.Dispose()}
 }
}finally{$original.Dispose();$target.Dispose()}
$aligned=Join-Path $output 'lab-aligned.apk'
& (Join-Path $build 'zipalign.exe') -f 4 $unsigned $aligned
if($LASTEXITCODE -ne 0){throw 'Numerical lab alignment failed'}
$signed=Join-Path $output 'Calibration-emulator-only.apk'
$key=Join-Path $workspace 'android/dist/gait-main-native/android/app/debug.keystore'
& (Join-Path $build 'apksigner.bat') sign --ks $key --ks-pass pass:android --key-pass pass:android --out $signed $aligned
if($LASTEXITCODE -ne 0){throw 'Numerical lab signing failed'}
$info=@{kind='separate-emulator-numerical-test';sourceApkSha256=(Get-FileHash $apk).Hash;testApkSha256=(Get-FileHash $signed).Hash;physicalPhoneRelease=$false;mockedNumericalSolver=$false;builtAt=(Get-Date).ToString('o')}
$info | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'build.json') -Encoding UTF8
Write-Output "Numerical test APK ready: $signed"
