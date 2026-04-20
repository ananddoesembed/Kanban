# Project Plan

This document is the execution plan for the Project Management MVP. It breaks the work into phases with concrete checklists, tests, success criteria, and approval gates.

## Planning assumptions

- The source of truth for product scope is the top-level AGENTS.md.
- The repository did not initially contain a frontend/ directory, so the frontend was created in-repo during Part 3.
- design.md now provides the approved visual direction for the frontend shell.
- The original repo gaps were resolved by explicit approval before implementation continued.

## Global engineering rules

- Keep the solution minimal and MVP-scoped.
- Fix root causes, not symptoms.
- Avoid introducing infrastructure that is not required by the stated business requirements.
- Keep docs short and operational.
- Prefer deterministic tests that run locally.
- Add approval checkpoints before any schema or architecture decisions that are hard to unwind.

## Phase checklist legend

- [ ] Not started
- [x] Completed
- Approval gates must be reviewed by the user before moving to the next phase.

## Part 1: Plan and repo alignment

### Goal

Produce an approved implementation plan and reconcile planning assumptions with the actual repository state.

### Checklist

- [x] Review top-level instructions and project constraints.
- [x] Review docs/PLAN.md and replace the stub with a detailed plan.
- [x] Verify whether frontend/ exists in the repository.
- [x] Verify whether design.md contains usable guidance.
- [x] Confirm with the user whether the existing frontend should be added to this repo or rebuilt here.
- [ ] If frontend code is added to the repo before implementation starts, create frontend/AGENTS.md describing that codebase.
- [x] If frontend code is added to the repo before implementation starts, create frontend/AGENTS.md describing that codebase.
- [x] Obtain explicit user approval on this plan before starting implementation work.

### Tests

- Manual verification that this document reflects the actual repository contents.
- Manual verification that open questions and assumptions are explicit.

### Success criteria

- The user can approve this plan without ambiguity about scope or sequencing.
- Known repo mismatches are documented instead of being silently ignored.
- The next implementation step is clear and bounded.

### Approval gate

User approves the plan and confirms how to handle the missing frontend/ source.

## Part 2: Scaffolding

### Goal

Create the minimal runnable full-stack scaffold: Docker packaging, FastAPI backend, startup scripts, and a verified hello-world path for both HTML and API.

### Checklist

- [x] Create backend project structure under backend/.
- [x] Initialize Python project metadata using uv-compatible conventions.
- [x] Add FastAPI app entrypoint with health and sample API routes.
- [x] Serve a minimal static HTML response from / as a temporary scaffold.
- [x] Add Dockerfile and any required container config.
- [x] Add local environment loading for .env values needed by later phases.
- [x] Create start scripts for Windows, macOS, and Linux in scripts/.
- [x] Create stop scripts for Windows, macOS, and Linux in scripts/.
- [x] Document the minimum run flow in backend/AGENTS.md and scripts/AGENTS.md.

### Tests

- Build the Docker image successfully.
- Start the container with the provided scripts.
- Verify GET / returns the scaffold HTML.
- Verify a sample backend route such as GET /api/health returns JSON.
- Verify stop scripts shut down the app cleanly.

### Success criteria

- A new developer can start the project locally with the provided scripts.
- The app runs in Docker and serves both HTML and JSON.
- The scaffold is minimal and ready to host the real frontend.

## Part 3: Add frontend

### Goal

Create or import the frontend and make it build cleanly within the full-stack project structure.

### Checklist

- [x] Resolve whether frontend/ is imported from an existing MVP or created fresh in this repo.
- [x] Create frontend/ if it does not exist.
- [x] Add frontend/AGENTS.md describing the frontend structure, commands, and key decisions.
- [x] Set up the React or Next.js frontend according to the approved direction.
- [x] Ensure the frontend can be built for production.
- [x] Integrate the frontend build output with FastAPI serving at /.
- [x] Apply the project color palette where appropriate.

### Tests

- Frontend install succeeds.
- Frontend production build succeeds.
- FastAPI serves the built frontend at /.
- Loading the app in a browser renders the frontend shell instead of the placeholder HTML.

### Success criteria

- The repository contains a working frontend/ directory.
- The frontend is served by the backend in the Dockerized flow.
- The project has a documented frontend structure and entrypoints.

### Approval gate

If a fresh frontend must be created because the prior MVP is unavailable, confirm that direction with the user before implementation.

## Part 4: Fake sign-in experience

### Goal

Gate the Kanban UI behind a simple local sign-in flow using the fixed MVP credentials.

### Checklist

- [x] Add a login screen at the initial app entry.
- [x] Validate only user/password for the MVP.
- [x] Add logout support.
- [x] Persist session state only as much as needed for local MVP behavior.
- [x] Prevent direct access to the Kanban UI when signed out.
- [x] Show clear error messaging for invalid credentials.

### Tests

- Frontend tests for login form behavior.
- Frontend tests for successful login with user/password.
- Frontend tests for failed login with invalid credentials.
- Frontend tests for logout returning the user to the login screen.
- Browser smoke test that / shows login first and Kanban only after sign-in.

### Success criteria

- The Kanban cannot be accessed until the user signs in.
- The only accepted MVP credentials are user/password.
- Logout reliably clears the session and returns to login.

## Part 5: Database modeling

### Goal

Define and document the simplest durable schema that supports one board per user while allowing future multi-user growth.

### Checklist

- [x] Propose SQLite schema for users, boards, and board state.
- [x] Decide how Kanban state is stored as JSON.
- [x] Decide whether chat history is stored now or deferred to a later phase.
- [x] Document migration and database file creation behavior.
- [x] Write a short architecture note in docs/ explaining the schema and tradeoffs.
- [x] Obtain user sign-off before implementation.

### Tests

- Manual schema review against business requirements.
- Optional lightweight schema creation test proving tables can be created from scratch.

### Success criteria

- The schema supports the MVP without over-modeling.
- The data model is documented clearly enough to implement backend routes.
- The user approves the storage approach before code is written.

### Approval gate

User approves the documented database approach.

## Part 6: Backend API

### Goal

Implement persistence and API routes for loading and mutating a user's Kanban board.

### Checklist

- [x] Add SQLite initialization on app startup if the database file does not exist.
- [x] Implement storage access layer for board reads and writes.
- [x] Add API route to fetch the signed-in user's board.
- [x] Add API route to replace or update board state.
- [x] Keep the API shape simple and aligned with frontend needs.
- [x] Add backend tests covering normal and failure paths.

### Tests

- Unit tests for database initialization.
- Unit tests for repository or service-layer board read/write behavior.
- API tests for successful board fetch.
- API tests for successful board update.
- API tests for invalid payload handling.

### Success criteria

- Starting from an empty environment creates a usable database automatically.
- The backend can persist and return board state for the MVP user.
- The API is stable enough for frontend integration.

## Part 7: Frontend and backend integration

### Goal

Replace mock or local-only Kanban state with live backend-backed persistence.

### Checklist

- [x] Load board state from the backend after sign-in.
- [x] Persist card edits, moves, and column renames through the backend.
- [x] Add loading and error states around board fetch and save operations.
- [x] Ensure the initial user experience works cleanly with an empty board.
- [x] Keep optimistic updates minimal unless clearly needed.

### Tests

- Frontend integration tests for initial board load.
- Frontend integration tests for editing and saving a card.
- Frontend integration tests for drag-and-drop persistence.
- End-to-end smoke test of login, board load, edit, refresh, and persisted state.

### Success criteria

- Refreshing the app preserves board changes.
- The frontend is no longer a disconnected demo.
- Error handling is adequate for local MVP use.

## Part 8: AI connectivity

### Goal

Prove backend connectivity to OpenRouter with the configured model before introducing Kanban mutation logic.

### Checklist

- [x] Add backend configuration for OPENROUTER_API_KEY.
- [x] Add a thin client wrapper for OpenRouter requests.
- [x] Use openai/gpt-oss-120b as the configured model.
- [x] Add a simple backend path or test utility that asks the model 2+2.
- [x] Fail clearly when the API key is missing.

### Tests

- Unit test for configuration validation.
- Integration test or manual verification for a successful 2+2 response.
- Manual verification that missing credentials produce a clear error.

### Success criteria

- The backend can successfully call OpenRouter.
- Model selection is explicit and configurable from one place.
- Connectivity issues are diagnosable quickly.

## Part 9: AI board-aware structured output

### Goal

Have the backend send board context and conversation history to the model and receive validated structured outputs that may include a board update.

### Checklist

- [x] Define the structured output schema for chat reply plus optional board mutation.
- [x] Include current board JSON in the AI request.
- [x] Include conversation history in the AI request.
- [x] Validate model responses against the schema before applying updates.
- [x] Apply optional board updates server-side only after validation.
- [x] Persist both the assistant reply and any accepted board mutation as required by the chosen storage approach.

### Tests

- Unit tests for schema validation.
- Unit tests for handling replies with no board mutation.
- Unit tests for handling valid board mutation payloads.
- Unit tests for rejecting malformed AI outputs.
- Integration test covering request, model response parsing, and board persistence.

### Success criteria

- The AI response format is deterministic enough for backend use.
- Invalid model output does not corrupt board state.
- Valid model-suggested updates can safely modify the Kanban.

## Part 10: AI chat sidebar UI

### Goal

Add the final AI chat experience to the frontend and keep the Kanban synchronized when AI-driven updates occur.

### Checklist

- [x] Design and implement a sidebar chat UI aligned with the project visual direction.
- [x] Render conversation history in the sidebar.
- [x] Submit user prompts to the backend AI endpoint.
- [x] Show assistant responses and loading states.
- [x] Refresh or update the board automatically when the backend returns a board change.
- [x] Handle AI errors without breaking the Kanban UI.

### Tests

- Frontend tests for chat submission and message rendering.
- Frontend tests for loading and error states.
- Integration test proving AI-driven board updates refresh the visible Kanban.
- End-to-end smoke test covering login, board view, chat request, and board mutation.

### Success criteria

- The user can chat with the assistant from the sidebar.
- AI-driven board changes appear in the Kanban without manual reload.
- The final UI remains stable and usable on desktop and mobile.

## Recommended execution order

1. Approve this plan and resolve the missing frontend question.
2. Complete scaffolding first so there is a stable run loop.
3. Add or import the frontend before implementing sign-in.
4. Approve the database design before backend persistence work.
5. Integrate backend persistence before any AI work.
6. Add AI connectivity before structured outputs.
7. Add the chat sidebar only after the backend AI contract is stable.

## Open questions requiring user confirmation

1. Should the missing frontend MVP be added into this repository, or should it be recreated here from scratch?
2. Should the frontend stack be Next.js, as stated in AGENTS.md, or a plain React app, as implied by the original stub text?
3. Should chat history be stored in SQLite for the MVP, or can it remain in-memory until a later phase?

## Approval

Implementation should not begin until the user explicitly approves this plan and answers the open questions above.