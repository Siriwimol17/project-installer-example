$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = (Resolve-Path $repoRoot).Path
$devData = Join-Path $repoRoot '.devdata'
New-Item -ItemType Directory -Force -Path $devData | Out-Null

$common = @{
    INTERNAL_TOKEN = 'dev-token'
    DATA_DIR = $devData
}

function Start-DevService {
    param(
        [Parameter(Mandatory)] [string] $Name,
        [Parameter(Mandatory)] [string] $WorkingDirectory,
        [Parameter(Mandatory)] [string] $Executable,
        [Parameter(Mandatory)] [string[]] $Arguments,
        [Parameter(Mandatory)] [string[]] $RequiredPaths,
        [Parameter(Mandatory)] [hashtable] $Environment
    )

    foreach ($path in $RequiredPaths) {
        if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $path))) {
            Write-Warning "$Name skipped: required path '$path' does not exist yet."
            return
        }
    }

    $envLines = foreach ($entry in $Environment.GetEnumerator()) {
        "$($entry.Key)='$($entry.Value)'"
    }
    $envSetup = $envLines -join '; '
    $quotedArgs = $Arguments | ForEach-Object { "'" + ($_ -replace "'", "''") + "'" }
    $commandLine = "Set-Location -LiteralPath '$($WorkingDirectory -replace "'", "''")'; $envSetup; & '$Executable' $($quotedArgs -join ' ')"
    Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoExit','-ExecutionPolicy','Bypass','-Command',$commandLine) -WorkingDirectory $WorkingDirectory
    Write-Host "Started $Name in a separate terminal window."
}

$dotnetSvcEnv = $common.Clone()
$dotnetSvcEnv.PORT = '5101'
Start-DevService -Name 'DotnetSvc' -WorkingDirectory (Join-Path $repoRoot 'src/DotnetSvc') -Executable 'dotnet' -Arguments @('run','--project','src/DotnetSvc') -RequiredPaths @('src/DotnetSvc','src/DotnetSvc/DotnetSvc.csproj') -Environment $dotnetSvcEnv

$pySvcEnv = $common.Clone()
$pySvcEnv.PORT = '5102'
Start-DevService -Name 'py-svc' -WorkingDirectory (Join-Path $repoRoot 'src/py-svc') -Executable 'python' -Arguments @('src/py-svc/main.py') -RequiredPaths @('src/py-svc','src/py-svc/main.py') -Environment $pySvcEnv

$webApiEnv = $common.Clone()
$webApiEnv.PORT = '5000'
$webApiEnv.DOTNET_SVC_URL = 'http://127.0.0.1:5101'
$webApiEnv.PY_SVC_URL = 'http://127.0.0.1:5102'
Start-DevService -Name 'WebApi' -WorkingDirectory (Join-Path $repoRoot 'src/WebApi') -Executable 'dotnet' -Arguments @('run','--project','src/WebApi') -RequiredPaths @('src/WebApi','src/WebApi/WebApi.csproj') -Environment $webApiEnv
