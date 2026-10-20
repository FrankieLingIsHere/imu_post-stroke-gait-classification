# Build the same app source for the emulator's CPU. Never changes release records.
$ErrorActionPreference='Stop'
$workspace=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$env:JAVA_HOME=Join-Path $workspace 'android/dist/native-distance-tools/jdk-17.0.20.1+1'
$env:ANDROID_HOME=Join-Path $workspace 'android/dist/native-distance-tools/android-sdk'
$env:GRADLE_USER_HOME=Join-Path $env:USERPROFILE '.gait-gradle-cache'
$env:NODE_ENV='production'
$output=Join-Path $workspace 'android/dist/emulator-lab'
$shortBuild=Join-Path $env:USERPROFILE '.gait-mobile-native'
New-Item -ItemType Directory -Force -Path $output,$shortBuild | Out-Null
$native=Join-Path $workspace 'android/modules/gait-camera-calibration/android'
$prior=Join-Path $native '.cxx/RelWithDebInfo/2660v4r1/arm64-v8a/_deps'
$upstreamConfig=(Get-Content -LiteralPath (Join-Path $native 'src/main/cpp/CMakeLists.txt') -Raw)+(Get-Content -LiteralPath (Join-Path $native 'src/main/cpp/openvins.cmake') -Raw)
$lines=@()
foreach($dep in @('eigen','ceres','vins','openvins','boost')){
  $source=Join-Path $prior "$dep-src"
  $stamp=Join-Path $prior "$dep-subbuild/$dep-populate-prefix/src/$dep-populate-stamp/$dep-populate-urlinfo.txt"
  $url=[regex]::Match($upstreamConfig,"FetchContent_Declare\($dep URL ([^\s)]+)").Groups[1].Value
  # Reuse only a cache that belongs to the currently pinned URL, not an older method.
  if((Test-Path -LiteralPath $source) -and (Test-Path -LiteralPath $stamp) -and $url -and (Get-Content -LiteralPath $stamp -Raw).Contains($url)){
    $lines+="android.defaultConfig.externalNativeBuild.cmake.arguments.add('-DFETCHCONTENT_SOURCE_DIR_$($dep.ToUpper())=$($source.Replace('\','/'))')"
  }
}
$shortPath=$shortBuild.Replace('\','/')
$extra=$lines -join "`n"
$init=@"
gradle.beforeProject { p ->
  p.tasks.configureEach { task ->
    if (task.name == 'createReleaseUpdatesResources') task.outputs.upToDateWhen { false }
    // Lab runs must use this APK's bundle, never a previously downloaded preview OTA.
    if (task.name == 'processReleaseManifest') {
      task.outputs.upToDateWhen { false }
      task.doLast {
        task.outputs.files.asFileTree.matching { include '**/AndroidManifest.xml' }.each { manifest ->
          def text = manifest.getText('UTF-8')
          text = text.replaceAll(/(<meta-data\s+android:name="expo.modules.updates.ENABLED"\s+android:value=")true("\s*\/>)/, '`$1false`$2')
          manifest.write(text, 'UTF-8')
        }
      }
    }

  }
  p.plugins.withId('com.android.application') {
    p.extensions.getByName('androidComponents').finalizeDsl { android ->
      android.defaultConfig.ndk.abiFilters.clear()
      android.defaultConfig.ndk.abiFilters.add('x86_64')
    }
  }
  p.plugins.withId('com.android.library') {
    if (p.name in ['gait-camera-calibration', 'expo-modules-core']) {
      p.extensions.getByName('androidComponents').finalizeDsl { android ->
        android.externalNativeBuild.cmake.buildStagingDirectory = new File('$shortPath/' + p.name)
        if (p.name == 'gait-camera-calibration') {
          $extra
        }
      }
    }
  }
}
"@
$initPath=Join-Path $output 'emulator-native.init.gradle'
[IO.File]::WriteAllText($initPath,$init)
function Restore-LabUpdateManifest {
  param([string]$ManifestPath)
  if(Test-Path -LiteralPath $ManifestPath){
    $text=Get-Content -LiteralPath $ManifestPath -Raw
    $restored=[regex]::Replace($text,'(android:name="expo.modules.updates.ENABLED"\s+android:value=")false(")','${1}true${2}')
    if($restored -ne $text){[IO.File]::WriteAllText($ManifestPath,$restored,[Text.UTF8Encoding]::new($false))}
  }
}
$project=Join-Path $workspace 'android/dist/gait-main-native/android'
try {
& (Join-Path $project 'gradlew.bat') -p $project --init-script $initPath :app:assembleRelease -PreactNativeArchitectures=x86_64 --offline --console=plain
if($LASTEXITCODE -ne 0){throw 'Emulator APK build failed. Inspect build logs; do not publish it as a phone release.'}
$apk=Join-Path $output 'GaitTrace-emulator-x86_64.apk'
Copy-Item -LiteralPath (Join-Path $project 'app/build/outputs/apk/release/app-release.apk') -Destination $apk
Add-Type -AssemblyName System.IO.Compression.FileSystem
$archive=[IO.Compression.ZipFile]::OpenRead($apk)
try {
  foreach($library in @('libhermes.so','libreactnative.so','libexpo-modules-core.so','libgait_openvins.so','libgait_phone_vio.so','libopencv_java4.so')){
    if(!$archive.GetEntry("lib/x86_64/$library")){throw "Emulator package missing x86_64/$library; do not install it."}
  }
} finally {$archive.Dispose()}
$mergedManifest=Join-Path $project 'app/build/intermediates/merged_manifests/release/processReleaseManifest/AndroidManifest.xml'
$manifestXml=[xml](Get-Content -LiteralPath $mergedManifest -Raw)
$updatesEntry=$manifestXml.manifest.application.'meta-data' | Where-Object { $_.GetAttribute('name','http://schemas.android.com/apk/res/android') -eq 'expo.modules.updates.ENABLED' }
if($updatesEntry.GetAttribute('value','http://schemas.android.com/apk/res/android') -ne 'false'){throw 'Lab APK could load cached OTA code instead of the tested bundle.'}
$manifest=Get-Content -LiteralPath (Join-Path $project 'app/build/generated/assets/createReleaseUpdatesResources/app.manifest') -Raw | ConvertFrom-Json
$bundle=Join-Path $project 'app/build/generated/assets/createBundleReleaseJsAndAssets/index.android.bundle'
$info=@{kind='emulator-only-apk';architecture='x86_64';apk=$apk;sha256=(Get-FileHash -LiteralPath $apk -Algorithm SHA256).Hash;embeddedUpdateId=$manifest.id;bundleSha256=(Get-FileHash -LiteralPath $bundle -Algorithm SHA256).Hash;physicalPhoneRelease=$false;previewOtaEnabled=$false;builtAt=(Get-Date).ToString('o')}
$info | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'emulator-apk.json') -Encoding UTF8
Write-Host "Emulator-only APK ready: $apk"
} finally {
  # Invalidate the lab-modified Gradle output so a later phone build regenerates
  # its enabled update manifest instead of reusing the emulator-only setting.
  Restore-LabUpdateManifest -ManifestPath (Join-Path $project 'app/build/intermediates/merged_manifests/release/processReleaseManifest/AndroidManifest.xml')
}
exit 0
