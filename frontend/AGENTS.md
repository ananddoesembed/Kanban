## Frontend

This folder contains the frontend for the Project Management MVP.

Current stack:

- Next.js App Router
- Static export build for FastAPI to serve
- React 19

Current contents:

- app/layout.js: root layout and metadata
- app/page.js: Cobalt Kinetic Kanban shell with five fixed columns
- app/globals.css: global styling based on the design brief in design.md
- next.config.mjs: static export configuration
- package.json: frontend scripts and dependencies

Current scope:

- Render a polished Kanban shell aligned to the approved visual direction
- Build to static assets for backend serving
- Provide the base UI for upcoming login, persistence, and AI features