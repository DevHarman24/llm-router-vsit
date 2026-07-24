"""
Vercel Serverless Entry Point
Imports the FastAPI app, wires in the correct paths, and mounts
the frontend static files using an absolute path so they resolve
correctly on Vercel's serverless filesystem.
"""

import sys
import os

# ── Path setup ───────────────────────────────────────────────────────────────
# PROJECT_ROOT resolves to the repo root regardless of where Vercel places the file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Tell server.py we are on Vercel (suppresses its own StaticFiles mount)
os.environ["VERCEL"] = "1"

# ── Import the FastAPI app ────────────────────────────────────────────────────
from backend.server import app  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

# ── Mount frontend with an absolute path ─────────────────────────────────────
# Relative paths break on Vercel; absolute path always resolves correctly.
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
