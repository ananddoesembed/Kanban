$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..")
$imageName = "pm-mvp"
$containerName = "pm-mvp"
$envFile = Join-Path $repoRoot ".env"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is required but was not found on PATH."
}

cmd /c "docker container inspect $containerName >nul 2>&1"
if ($LASTEXITCODE -eq 0) {
    cmd /c "docker rm -f $containerName >nul 2>&1"
}

docker build -t $imageName $repoRoot

$runArgs = @(
    "run",
    "--detach",
    "--name", $containerName,
    "-p", "8000:8000"
)

if (Test-Path $envFile) {
    $runArgs += @("--env-file", $envFile)
}

$runArgs += $imageName

docker @runArgs | Out-Null

Write-Host "Started http://localhost:8000"