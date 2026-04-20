@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "REPO_ROOT=%%~fI"
set "IMAGE_NAME=pm-mvp"
set "CONTAINER_NAME=pm-mvp"

where docker >nul 2>nul
if errorlevel 1 (
  echo Docker is required but was not found on PATH.
  exit /b 1
)

docker rm -f %CONTAINER_NAME% >nul 2>nul
docker build -t %IMAGE_NAME% "%REPO_ROOT%"
if errorlevel 1 exit /b 1

if exist "%REPO_ROOT%\.env" (
  docker run --detach --name %CONTAINER_NAME% --env-file "%REPO_ROOT%\.env" -p 8000:8000 %IMAGE_NAME% >nul
) else (
  docker run --detach --name %CONTAINER_NAME% -p 8000:8000 %IMAGE_NAME% >nul
)

if errorlevel 1 exit /b 1

echo Started http://localhost:8000