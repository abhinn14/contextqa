# Contextrag

Guides for running the frontend (Next.js) and backend (FastAPI) parts of this project.

## Prerequisites
- Node.js 20+
- pnpm (recommended) or npm
- Python 3.10+
- (Optional) uv or pipx for creating virtual environments

## Frontend (Next.js)
### Setup
1. `cd frontend`
2. Install deps (choose one):
   - `pnpm install`
   - `npm install`

### Run
- Dev server: `pnpm dev` (or `npm run dev`)
- Open: http://localhost:3000

### Build & Preview
- Build: `pnpm build` (or `npm run build`)
- Preview production build: `pnpm start` (or `npm run start`)

## Backend (FastAPI)
Project root: `rag-2`

### Setup environment
1. `cd rag-2`
2. Create venv (pick one):
   - `python -m venv .venv && .venv\Scripts\activate`
   - `uv venv && .venv\Scripts\activate` (if uv installed)
3. Install deps:
   - `pip install -r requirements.txt`
   - or with uv: `uv pip install -r requirements.txt`

### Run API
- `uvicorn main:app --reload`
- Default URL: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

## Concurrent Dev (optional)
- Run backend: `cd rag-2 && uvicorn main:app --reload`
- In another terminal, run frontend: `cd frontend && pnpm dev`

## Troubleshooting
- If Node deps fail, remove lockfile and `node_modules`, then reinstall.
- If Python packages fail, ensure the venv is active and pip is recent: `python -m pip install --upgrade pip`.
- Port in use? Change with `--port` for uvicorn or `-p`/`--port` for Next dev server.
