"""
Temporal query route.

Returns the time-series history of SAR change detection events for a given
latitude / longitude coordinate.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from spatial_api.app.core.postgis_client import get_db

router = APIRouter(prefix="/temporal", tags=["temporal"])


class ChangeEvent(BaseModel):
    """A single change-detection event record."""

    id: int
    detected_at: str
    area_sqkm: float = Field(..., description="Area of the changed region in square kilometres.")


class TimeSeriesResponse(BaseModel):
    """Time-series response envelope."""

    lat: float
    lon: float
    events: List[ChangeEvent]


@router.get(
    "/history",
    response_model=TimeSeriesResponse,
    summary="Query the change-detection history at a point",
)
async def get_history(
    lat: float,
    lon: float,
    db: AsyncSession = Depends(get_db),
) -> TimeSeriesResponse:
    """
    Return all historical change-detection events that contain the given point.

    Args:
        lat: Latitude in WGS-84 decimal degrees (−90 to 90).
        lon: Longitude in WGS-84 decimal degrees (−180 to 180).
        db: Injected async database session.

    Returns:
        A :class:`TimeSeriesResponse` with the full list of matching events
        ordered by detection date.

    Raises:
        HTTPException(400): If coordinates are out of range.
    """
    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail="lat must be between -90 and 90.")
    if not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="lon must be between -180 and 180.")

    query = text(
        """
        SELECT id, detected_at::text, area_sqkm
        FROM change_polygons
        WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
        ORDER BY detected_at ASC
        """
    )

    result = await db.execute(query, {"lat": lat, "lon": lon})
    rows = result.fetchall()

    events = [
        ChangeEvent(id=row.id, detected_at=row.detected_at, area_sqkm=row.area_sqkm)
        for row in rows
    ]
    return TimeSeriesResponse(lat=lat, lon=lon, events=events)
