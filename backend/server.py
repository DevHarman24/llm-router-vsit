"""
FastAPI Backend Server for LLM Router
"""

import os
import base64
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from router.engine import route
from router.models import get_catalog, ModelInfo

app = FastAPI(title="LLM Router API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RouteRequest(BaseModel):
    query: str
    has_image: bool = False
    has_file: bool = False
    file_size_kb: float = 0
    mode: str = "standard"


class RouteResponse(BaseModel):
    model_id: str
    model_name: str
    provider: str
    tier: int
    tier_label: str
    price_per_million_tokens: float
    context_window: int
    supports_vision: bool
    supports_thinking: bool
    supports_coding: bool
    needs_vision: bool
    needs_thinking: bool
    needs_coding: bool
    total_time_ms: float
    heuristic_time_ms: float
    llm_time_ms: float
    llm_used: bool
    signals: list[str]
    reasoning: str
    classifier_source: Optional[str] = None
    mode: str = "standard"


@app.post("/api/route", response_model=RouteResponse)
async def route_query(request: RouteRequest):
    """Route a text query to the best model."""
    groq_key = os.getenv("GROQ_API_KEY", "")
    decision = route(
        query=request.query,
        has_image=request.has_image,
        has_file=request.has_file,
        file_size_kb=request.file_size_kb,
        groq_api_key=groq_key or None,
        mode=request.mode,
    )
    return RouteResponse(
        model_id=decision.model.id,
        model_name=decision.model.name,
        provider=decision.model.provider,
        tier=decision.tier,
        tier_label=decision.tier_label,
        price_per_million_tokens=decision.model.price_per_million_tokens,
        context_window=decision.model.context_window,
        supports_vision=decision.model.supports_vision,
        supports_thinking=decision.model.supports_thinking,
        supports_coding=decision.model.supports_coding,
        needs_vision=decision.needs_vision,
        needs_thinking=decision.needs_thinking,
        needs_coding=decision.needs_coding,
        total_time_ms=round(decision.total_time_ms, 2),
        heuristic_time_ms=round(decision.heuristic_time_ms, 2),
        llm_time_ms=round(decision.llm_time_ms, 2),
        llm_used=decision.llm_used,
        signals=decision.signals,
        reasoning=decision.reasoning,
        classifier_source=decision.classifier.source if decision.classifier else "heuristic",
        mode=request.mode,
    )


@app.post("/api/route-with-file", response_model=RouteResponse)
async def route_with_file(
    query: str = Form(...),
    file: Optional[UploadFile] = File(None),
    mode: str = Form("standard"),
):
    """Route a query that may include an uploaded file or image."""
    has_image = False
    has_file = False
    file_size_kb = 0.0

    if file and file.filename:
        content = await file.read()
        file_size_kb = len(content) / 1024
        image_types = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
        has_image = file.content_type in image_types
        has_file = not has_image

    groq_key = os.getenv("GROQ_API_KEY", "")
    decision = route(
        query=query,
        has_image=has_image,
        has_file=has_file,
        file_size_kb=file_size_kb,
        groq_api_key=groq_key or None,
        mode=mode,
    )

    return RouteResponse(
        model_id=decision.model.id,
        model_name=decision.model.name,
        provider=decision.model.provider,
        tier=decision.tier,
        tier_label=decision.tier_label,
        price_per_million_tokens=decision.model.price_per_million_tokens,
        context_window=decision.model.context_window,
        supports_vision=decision.model.supports_vision,
        supports_thinking=decision.model.supports_thinking,
        supports_coding=decision.model.supports_coding,
        needs_vision=decision.needs_vision,
        needs_thinking=decision.needs_thinking,
        needs_coding=decision.needs_coding,
        total_time_ms=round(decision.total_time_ms, 2),
        heuristic_time_ms=round(decision.heuristic_time_ms, 2),
        llm_time_ms=round(decision.llm_time_ms, 2),
        llm_used=decision.llm_used,
        signals=decision.signals,
        reasoning=decision.reasoning,
        classifier_source=decision.classifier.source if decision.classifier else "heuristic",
        mode=mode,
    )


@app.get("/api/models")
async def list_models():
    """Return the current model catalog with their tiers."""
    catalog = get_catalog()
    return [
        {
            "id": m.id,
            "name": m.name,
            "tier": m.tier,
            "provider": m.provider,
            "context_window": m.context_window,
            "price_per_million_tokens": m.price_per_million_tokens,
            "supports_vision": m.supports_vision,
            "supports_thinking": m.supports_thinking,
            "supports_coding": m.supports_coding,
        }
        for m in catalog
    ]


@app.get("/api/health")
async def health():
    return {"status": "ok", "groq_configured": bool(os.getenv("GROQ_API_KEY"))}


# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
