param(
    [string]$AppHost = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$NoReload
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

function Test-PythonModule {
    param(
        [string]$PythonExe,
        [string]$ModuleName
    )

    if (-not (Test-Path $PythonExe)) {
        return $false
    }

    try {
        & $PythonExe -c "import $ModuleName" *> $null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Resolve-PythonExe {
    $candidates = @(
        (Join-Path $repoRoot ".venv\\Scripts\\python.exe"),
        "C:\\Users\\Administrator\\.venv-presensi\\Scripts\\python.exe"
    )

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        $candidates += $python.Source
    }

    foreach ($candidate in $candidates) {
        if (Test-PythonModule -PythonExe $candidate -ModuleName "uvicorn") {
            return $candidate
        }
    }

    throw "Python tidak ditemukan. Siapkan virtual environment backend dulu."
}

$pythonExe = Resolve-PythonExe
$arguments = @("-m", "hris_bpe.dev", "--host", $AppHost, "--port", "$Port")

if ($NoReload) {
    $arguments += "--no-reload"
}

Write-Host "Menjalankan backend HRIS-BPE di http://$AppHost`:$Port"
Set-Location $repoRoot
$env:PYTHONPATH = "$repoRoot\\src" + $(if ($env:PYTHONPATH) { ";$env:PYTHONPATH" } else { "" })
& $pythonExe @arguments
