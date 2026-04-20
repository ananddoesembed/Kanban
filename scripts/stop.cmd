@echo off
setlocal

set "CONTAINER_NAME=pm-mvp"

where docker >nul 2>nul
if errorlevel 1 (
  echo Docker is required but was not found on PATH.
  exit /b 1
)

docker rm -f %CONTAINER_NAME% >nul 2>nul

echo Stopped %CONTAINER_NAME%