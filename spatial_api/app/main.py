"""
FastAPI application entry point for the SAR Spatial API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from spatial_api.app.api.routes.vector_tiles import router as tiles_router
from spatial_api.app.api.routes.temporal import router as temporal_router

app = FastAPI(
    title="SAR Observation Spatial API",
    description=(
        "High-performance query backend for SAR change detection results. "
        "Serves dynamic Mapbox Vector Tiles and temporal time-series data "
        "from a PostGIS spatial database."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tiles_router)
app.include_router(temporal_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Return a simple health-check response."""
    return {"status": "ok"}
