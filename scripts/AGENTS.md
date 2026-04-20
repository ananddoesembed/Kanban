## Scripts

This folder contains cross-platform helper scripts for running the app locally with Docker.

Current contents:

- start.ps1 and stop.ps1: PowerShell scripts for Windows
- start.cmd and stop.cmd: Command Prompt scripts for Windows
- start.sh and stop.sh: POSIX shell scripts for macOS and Linux

Current behavior:

- Build the Docker image from the repository root
- Run the app container on port 8000
- Load environment variables from .env when present
- Stop and remove the app container cleanly