param(
    [switch]$Fast,
    [switch]$FrontendOnly,
    [switch]$BackendOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"
$env:NEXT_TELEMETRY_DISABLED = "1"

if ($FrontendOnly -and $BackendOnly) {
    Write-Host "[FAIL] -FrontendOnly and -BackendOnly cannot be combined." -ForegroundColor Red
    exit 2
}

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$LogDirectory = Join-Path $ProjectRoot "logs"
New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null
$LogPath = Join-Path $LogDirectory "final_acceptance_latest.txt"
$script:Results = [ordered]@{}

function Protect-Output([string]$Line) {
    $safe = $Line -replace '(?i)(DB_PASSWORD\s*[=:]\s*)\S+', '$1[REDACTED]'
    $safe = $safe -replace '(?i)(mysql\+pymysql://)[^@\s]+@', '$1[REDACTED]@'
    $safe = $safe -replace '\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}', '[REDACTED_BCRYPT_HASH]'
    return $safe
}

function Write-Safe([string]$Line = "") {
    $safe = Protect-Output $Line
    Write-Host $safe
    Add-Content -Path $LogPath -Value $safe -Encoding UTF8
}

function Set-Result([string]$Name, [string]$Status) {
    $script:Results[$Name] = $Status
    $color = if ($Status.StartsWith("PASS")) { "Green" } elseif ($Status.StartsWith("SKIP")) { "Yellow" } else { "Red" }
    Write-Host "[$Status] $Name" -ForegroundColor $color
    Add-Content -Path $LogPath -Value "[$Status] $Name" -Encoding UTF8
}

function Invoke-Check {
    param(
        [string]$Name,
        [string]$File,
        [string[]]$Arguments = @(),
        [string]$WorkingDirectory = $ProjectRoot
    )
    Write-Safe ""
    Write-Safe "=== $Name ==="
    Push-Location $WorkingDirectory
    try {
        $output = & $File @Arguments 2>&1
        $code = $LASTEXITCODE
        foreach ($line in $output) { Write-Safe ([string]$line) }
    }
    catch {
        $code = 1
        Write-Safe ("Command could not start ({0})." -f $_.Exception.GetType().Name)
    }
    finally {
        Pop-Location
    }
    if ($code -eq 0) { Set-Result $Name "PASS"; return $true }
    Set-Result $Name "FAIL"; return $false
}

function Test-ProjectStructure {
    $required = @(
        "app.py", "requirements.txt", ".env.example", "api/main.py",
        "frontend/package.json", "frontend/package-lock.json", "frontend/app/login/page.tsx",
        "sql/01_schema.sql", "sql/03_views.sql", "sql/07_verification_queries.sql",
        "academic_demo/README.md", "academic_demo/sql/07_cursor_demo.sql",
        "academic_demo/sql/09_transactions_savepoints.sql",
        "academic_demo/sql/10_concurrency_demo.sql",
        "academic_demo/sql/12_dcl_roles_privileges.sql",
        "academic_demo/nosql/mongodb_demo.js",
        "docs/ETCS302_SYLLABUS_TRACEABILITY_MATRIX.md",
        "docs/DBMS_ACADEMIC_COVERAGE_REPORT.md",
        "docs/QUERY_OPTIMIZATION_REPORT.md",
        "docs/RBAC_PERMISSION_MATRIX.md",
        "docs/TRANSACTION_CONCURRENCY_RECOVERY_REPORT.md",
        "scripts/validate_project.py", "scripts/check_live_database.py",
        "scripts/test_database_safety.py", "scripts/scan_secrets.py"
    )
    $missing = @($required | Where-Object { -not (Test-Path (Join-Path $ProjectRoot $_) -PathType Leaf) })
    if ($missing.Count -gt 0) {
        Write-Safe ("Missing mandatory files: " + ($missing -join ", "))
        return $false
    }
    try {
        $package = Get-Content (Join-Path $ProjectRoot "frontend/package.json") -Raw | ConvertFrom-Json
        $scripts = @($package.scripts.PSObject.Properties.Name)
        $missingScripts = @("typecheck", "lint", "test", "build") | Where-Object { $_ -notin $scripts }
        if (@($missingScripts).Count -gt 0) {
            Write-Safe ("Missing frontend package scripts: " + ($missingScripts -join ", "))
            return $false
        }
    }
    catch {
        Write-Safe "frontend/package.json is not valid JSON."
        return $false
    }
    return $true
}

Set-Content -Path $LogPath -Value "SEMS Final Acceptance - sanitized evidence" -Encoding UTF8
Write-Safe ("Started: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss K"))
Write-Safe ("Mode: " + $(if ($Fast) { "FAST" } elseif ($FrontendOnly) { "FRONTEND ONLY" } elseif ($BackendOnly) { "BACKEND ONLY" } else { "COMPLETE" }))
Write-Safe "No database rebuild, reset, seed, DROP, ALTER or credential rewrite is performed."

Write-Safe ""
Write-Safe "PHASE 1 - ENVIRONMENT / STRUCTURE"
if (Test-ProjectStructure) { Set-Result "Environment / project structure" "PASS" } else { Set-Result "Environment / project structure" "FAIL" }

$Python = "python"
$WindowsVenvPython = Join-Path $ProjectRoot ".venv/Scripts/python.exe"
$PosixVenvPython = Join-Path $ProjectRoot ".venv/bin/python"
if (Test-Path $WindowsVenvPython) { $Python = $WindowsVenvPython }
elseif (Test-Path $PosixVenvPython) { $Python = $PosixVenvPython }

$PythonRuntime = Invoke-Check "Python runtime" $Python @("--version")
$NodeRuntime = $true
if (-not $BackendOnly) {
    $NodeRuntime = Invoke-Check "Node.js runtime" "node" @("--version")
    $NpmRuntime = Invoke-Check "npm runtime" "npm" @("--version")
    if (-not (Test-Path (Join-Path $ProjectRoot "frontend/node_modules"))) {
        if ($NodeRuntime -and $NpmRuntime) {
            $Dependencies = Invoke-Check "Frontend dependency restore" "npm" @("ci", "--no-audit") (Join-Path $ProjectRoot "frontend")
        } else {
            Set-Result "Frontend dependency restore" "FAIL"
        }
    } else {
        Set-Result "Frontend dependency restore" "PASS (already installed)"
    }
}

$DatabaseReady = $false
$TestTargetSafe = $false

if (-not $FrontendOnly) {
    Write-Safe ""
    Write-Safe "PHASE 2 - PYTHON / BACKEND STATIC VALIDATION"
    if ($PythonRuntime) {
        $BackendStatic = Invoke-Check "Python compile/import and SQL static contract" $Python @("scripts/validate_project.py", "--skip-tests")
    } else {
        Set-Result "Python compile/import and SQL static contract" "FAIL"
    }

    Write-Safe ""
    Write-Safe "PHASE 3 - DATABASE READINESS (READ ONLY)"
    if ($PythonRuntime) {
        $DatabaseReady = Invoke-Check "MySQL connectivity and frozen database objects" $Python @("scripts/check_live_database.py")
    } else {
        Set-Result "MySQL connectivity and frozen database objects" "FAIL"
    }

    Write-Safe ""
    Write-Safe "PHASE 4 - TEST DATABASE SAFETY"
    if ($PythonRuntime) {
        $TestTargetSafe = Invoke-Check "Dedicated _test database safety" $Python @("scripts/test_database_safety.py")
    } else {
        Set-Result "Dedicated _test database safety" "FAIL"
    }

    Write-Safe ""
    Write-Safe "PHASE 5 - PYTHON TESTING"
    if ($PythonRuntime -and $TestTargetSafe) {
        $PythonTests = Invoke-Check "Python backend tests" $Python @("-m", "pytest", "-q")
    } elseif ($PythonRuntime) {
        $IndependentTests = Invoke-Check "Server-independent Python diagnostics" $Python @("-m", "pytest", "-q", "-m", "not integration")
        Set-Result "Python backend tests" "FAIL (integration blocked by unsafe/missing test target)"
    } else {
        Set-Result "Python backend tests" "FAIL"
    }

    Write-Safe ""
    Write-Safe "PHASE 6 - API VALIDATION"
    if ($PythonRuntime) {
        $ApiImport = Invoke-Check "FastAPI import" $Python @("-c", "from api.main import app; assert app.title.startswith('Smart Electronics')")
        $ApiTests = Invoke-Check "FastAPI authentication / RBAC / contract tests" $Python @("-m", "pytest", "-q", "-m", "api")
    } else {
        Set-Result "FastAPI import" "FAIL"
        Set-Result "FastAPI authentication / RBAC / contract tests" "FAIL"
    }
} else {
    foreach ($name in @("Python compile/import and SQL static contract", "MySQL connectivity and frozen database objects", "Dedicated _test database safety", "Python backend tests", "FastAPI import", "FastAPI authentication / RBAC / contract tests")) { Set-Result $name "SKIP (FrontendOnly)" }
}

Write-Safe ""
Write-Safe "PHASE 7 - MODERN FRONTEND VALIDATION"
if (-not $BackendOnly) {
    $FrontendDirectory = Join-Path $ProjectRoot "frontend"
    $Typecheck = Invoke-Check "Frontend type-check" "npm" @("run", "typecheck") $FrontendDirectory
    $Lint = Invoke-Check "Frontend lint" "npm" @("run", "lint") $FrontendDirectory
    $Tooling = Invoke-Check "Frontend runtime and lint compatibility" "npm" @("run", "check:tooling") $FrontendDirectory
    $FrontendTests = Invoke-Check "Frontend tests" "npm" @("run", "test") $FrontendDirectory
    if ($Fast) {
        Set-Result "Production frontend build" "SKIP (-Fast; run the complete command before release)"
    } else {
        $FrontendBuild = Invoke-Check "Production frontend build" "npm" @("run", "build") $FrontendDirectory
    }
} else {
    foreach ($name in @("Frontend type-check", "Frontend lint", "Frontend runtime and lint compatibility", "Frontend tests", "Production frontend build")) { Set-Result $name "SKIP (BackendOnly)" }
}

Write-Safe ""
Write-Safe "PHASE 8 - SECURITY / SECRET HYGIENE"
if ($PythonRuntime) {
    $SecretScan = Invoke-Check "Secret hygiene" $Python @("scripts/scan_secrets.py")
    $PythonPackages = Invoke-Check "Python dependency consistency" $Python @("-m", "pip", "check")
} else {
    Set-Result "Secret hygiene" "FAIL"
    Set-Result "Python dependency consistency" "FAIL"
}
if (-not $BackendOnly) {
    $NpmAudit = Invoke-Check "Frontend npm runtime and reviewed dev audit" $Python @("scripts/check_npm_audit.py")
} else {
    Set-Result "Frontend npm runtime and reviewed dev audit" "SKIP (BackendOnly)"
}

Write-Safe ""
Write-Safe "============================================================"
Write-Safe "SEMS FINAL ACCEPTANCE"
Write-Safe "============================================================"
foreach ($item in $script:Results.GetEnumerator()) {
    Write-Safe ("[{0}] {1}" -f $item.Value, $item.Key)
}
$Failures = @($script:Results.GetEnumerator() | Where-Object { $_.Value.StartsWith("FAIL") }).Count
Write-Safe "------------------------------------------------------------"
if ($Failures -eq 0) {
    if ($Fast) { Write-Safe "FINAL RESULT: PASS (FAST MODE - PRODUCTION BUILD NOT ACCEPTED)" }
    elseif ($FrontendOnly) { Write-Safe "FINAL RESULT: PASS (FRONTEND-ONLY SCOPE)" }
    elseif ($BackendOnly) { Write-Safe "FINAL RESULT: PASS (BACKEND-ONLY SCOPE)" }
    else { Write-Safe "FINAL RESULT: PASS" }
    Write-Safe "------------------------------------------------------------"
    Write-Safe ("Sanitized log: " + $LogPath)
    exit 0
}
Write-Safe "FINAL RESULT: FAIL"
Write-Safe "------------------------------------------------------------"
Write-Safe ("Failed checks: " + $Failures)
Write-Safe ("Sanitized log: " + $LogPath)
exit 1
