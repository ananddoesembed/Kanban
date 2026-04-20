$ErrorActionPreference = "Stop"

$containerName = "pm-mvp"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is required but was not found on PATH."
}

cmd /c "docker container inspect $containerName >nul 2>&1"
if ($LASTEXITCODE -eq 0) {
    cmd /c "docker rm -f $containerName >nul 2>&1"
}

Write-Host "Stopped $containerName"