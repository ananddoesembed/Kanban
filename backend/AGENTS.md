## Backend

This folder contains the FastAPI backend for the Project Management MVP.

Current contents:

- app/main.py: FastAPI app entrypoint with starter routes for /, /api/health, and /api/hello
- tests/test_app.py: pytest coverage for the scaffold routes
- pyproject.toml: Python project metadata and dependencies used by uv in Docker

Current scope:

- Serve a temporary HTML scaffold from /
- Provide JSON starter endpoints for health and hello-world checks
- Act as the base for later database, auth, and AI work