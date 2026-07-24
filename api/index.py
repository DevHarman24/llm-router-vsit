"""
Vercel Serverless Entry Point
Imports the FastAPI app and exposes it for Vercel's Python runtime.
"""

import sys
import os

# Add project root to Python path so 'backend' and 'router' modules resolve correctly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Signal to server.py that we are running on Vercel (skips StaticFiles mount)
os.environ.setdefault("VERCEL", "1")

from backend.server import app  # noqa: F401 — Vercel picks up the `app` object
