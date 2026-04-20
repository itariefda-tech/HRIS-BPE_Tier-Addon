param(
    [string]$FlutterSdkPath,
    [string]$ApiBaseUrl,
    [string]$DeviceId,
    [switch]$SkipCreate,
    [switch]$SkipPubGet
)

$ErrorActionPreference = "Stop"

$mobileRoot = Split-Path -Parent $PSScriptRoot
$androidSdkRoot = "C:\\Android\\Sdk"
$javaHome = "C:\\Program Files\\Eclipse Adoptium\\jdk-17.0.17.10-hotspot"

function Resolve-FlutterBat {
    param([string]$SdkPath)

    $candidates = New-Object System.Collections.Generic.List[string]

    if ($SdkPath) {
        if ($SdkPath.EndsWith("flutter.bat", [System.StringComparison]::OrdinalIgnoreCase)) {
            $candidates.Add($SdkPath)
        } else {
            $candidates.Add((Join-Path $SdkPath "bin\\flutter.bat"))
        }
    }

    if ($env:FLUTTER_HOME) {
        $candidates.Add((Join-Path $env:FLUTTER_HOME "bin\\flutter.bat"))
    }

    $flutterFromPath = Get-Command flutter -ErrorAction SilentlyContinue
    if ($flutterFromPath) {
        $candidates.Add($flutterFromPath.Source)
    }

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path $candidate)) {
            return $candidate
        }
    }

    throw "Flutter SDK belum ditemukan. Pasang Flutter SDK atau kirim -FlutterSdkPath ke folder SDK."
}

function Get-PreferredApiBaseUrl {
    $preferred = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object {
            $_.IPAddress -notlike "127.*" -and
            $_.IPAddress -notlike "169.254*" -and
            $_.InterfaceAlias -match "Wi-Fi|Ethernet"
        } |
        Select-Object -First 1

    if (-not $preferred) {
        $preferred = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
            Where-Object {
                $_.IPAddress -notlike "127.*" -and
                $_.IPAddress -notlike "169.254*" -and
                $_.InterfaceAlias -notmatch "ZeroTier"
            } |
            Select-Object -First 1
    }

    if (-not $preferred) {
        throw "Tidak bisa mendeteksi IP LAN lokal. Kirim -ApiBaseUrl manual."
    }

    return "http://$($preferred.IPAddress):8000/api/v1"
}

if (-not (Test-Path $androidSdkRoot)) {
    throw "Android SDK tidak ditemukan di $androidSdkRoot."
}

if (-not (Test-Path $javaHome)) {
    throw "JAVA_HOME tidak ditemukan di $javaHome."
}

$flutterBat = Resolve-FlutterBat -SdkPath $FlutterSdkPath

$env:ANDROID_SDK_ROOT = $androidSdkRoot
$env:ANDROID_HOME = $androidSdkRoot
$env:JAVA_HOME = $javaHome
$env:Path = "$androidSdkRoot\\platform-tools;$androidSdkRoot\\cmdline-tools\\latest\\bin;$javaHome\\bin;$env:Path"

if (-not $ApiBaseUrl) {
    $ApiBaseUrl = Get-PreferredApiBaseUrl
}

$backendListeners = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.LocalPort -eq 8000 }
$lanReady = $backendListeners |
    Where-Object { $_.LocalAddress -eq "0.0.0.0" -or $_.LocalAddress -eq "::" }

if (-not $lanReady) {
    Write-Warning "Backend port 8000 belum bind ke LAN. Jalankan ..\\scripts\\run-backend-lan.ps1 dulu agar device fisik bisa mengakses API."
}

$adbOutput = & (Join-Path $androidSdkRoot "platform-tools\\adb.exe") devices -l
if (-not ($adbOutput | Select-String -Pattern "\sdevice\s")) {
    Write-Warning "Belum ada device Android yang authorize di adb. Aktifkan USB debugging lalu approve RSA prompt di device."
}

Set-Location $mobileRoot

if (-not $SkipCreate -and -not (Test-Path (Join-Path $mobileRoot "android"))) {
    & $flutterBat create --platforms=android .
}

if (-not $SkipPubGet) {
    & $flutterBat pub get
}

$runArguments = @(
    "run",
    "--dart-define",
    "API_BASE_URL=$ApiBaseUrl"
)

if ($DeviceId) {
    $runArguments += @("-d", $DeviceId)
}

Write-Host "Menjalankan mobile guard ke $ApiBaseUrl"
& $flutterBat @runArguments
