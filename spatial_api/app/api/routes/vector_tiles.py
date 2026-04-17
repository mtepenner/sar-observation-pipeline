"""
Vector tiles route.

Serves dynamic Mapbox Vector Tiles (MVT) derived from the PostGIS change
detection polygons table.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from spatial_api.app.core.postgis_client import get_db

router = APIRouter(prefix="/tiles", tags=["vector-tiles"])


@router.get("/{z}/{x}/{y}.mvt", summary="Serve a Mapbox Vector Tile")
async def get_tile(
    z: int,
    x: int,
    y: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Return a binary Mapbox Vector Tile for the given tile coordinates.

    The tile is generated on-the-fly using PostGIS ``ST_AsMVT`` and
    ``ST_TileEnvelope`` functions against the ``change_polygons`` table.

    Args:
        z: Zoom level.
        x: Tile column index.
        y: Tile row index.
        db: Injected async database session.

    Returns:
        Binary MVT response with content-type ``application/x-protobuf``.
    """
    if not (0 <= z <= 22):
        raise HTTPException(status_code=400, detail="Zoom level must be between 0 and 22.")

    query = text(
        """
        SELECT ST_AsMVT(tile, 'changes', 4096, 'geom') AS mvt
        FROM (
            SELECT
                id,
                detected_at,
                area_sqkm,
                ST_AsMVTGeom(
                    geom,
                    ST_TileEnvelope(:z, :x, :y),
                    4096, 64, true
                ) AS geom
            FROM change_polygons
            WHERE geom && ST_TileEnvelope(:z, :x, :y)
        ) AS tile
        """
    )

    result = await db.execute(query, {"z": z, "x": x, "y": y})
    row = result.fetchone()

    if row is None or row.mvt is None:
        return Response(content=b"", media_type="application/x-protobuf")

    return Response(content=bytes(row.mvt), media_type="application/x-protobuf")
