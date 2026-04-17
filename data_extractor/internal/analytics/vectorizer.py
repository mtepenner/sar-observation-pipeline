"""
Vectorizer module.

Converts raster change masks (pixel grids) into searchable GeoJSON
vector polygons using rasterio's shapes API and geopandas.
"""

import json
from typing import Any, Dict, List

import numpy as np


def raster_mask_to_geojson(
    change_mask: np.ndarray,
    transform=None,
    crs: str = "EPSG:4326",
) -> Dict[str, Any]:
    """
    Convert a binary change mask into a GeoJSON FeatureCollection.

    Each connected polygon of True pixels becomes a GeoJSON Feature with a
    'change' property set to True.

    Args:
        change_mask: 2-D boolean array where True indicates a changed pixel.
        transform: An affine transform mapping pixel coordinates to geographic
                   coordinates. If None, pixel indices are used directly.
        crs: Coordinate Reference System string (e.g. 'EPSG:4326').

    Returns:
        A GeoJSON-compatible dict (FeatureCollection).
    """
    try:
        from rasterio.features import shapes as rio_shapes
        from rasterio.transform import from_bounds
        import rasterio
    except ImportError:
        return _fallback_geojson(change_mask)

    mask_uint8 = change_mask.astype(np.uint8)

    if transform is None:
        rows, cols = change_mask.shape
        transform = from_bounds(0, 0, cols, rows, cols, rows)

    features: List[Dict[str, Any]] = []
    for geom, val in rio_shapes(mask_uint8, mask=mask_uint8, transform=transform):
        if val == 1:
            features.append(
                {
                    "type": "Feature",
                    "geometry": geom,
                    "properties": {"change": True},
                }
            )

    return {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": crs}},
        "features": features,
    }


def _fallback_geojson(change_mask: np.ndarray) -> Dict[str, Any]:
    """
    Minimal fallback vectorizer using contiguous-region bounding boxes
    when rasterio is not available.
    """
    from scipy.ndimage import label as nd_label, find_objects

    labeled, n_labels = nd_label(change_mask)
    features: List[Dict[str, Any]] = []

    for region_slice in find_objects(labeled):
        if region_slice is None:
            continue
        row_start = region_slice[0].start
        row_stop = region_slice[0].stop
        col_start = region_slice[1].start
        col_stop = region_slice[1].stop

        coords = [
            [col_start, row_start],
            [col_stop, row_start],
            [col_stop, row_stop],
            [col_start, row_stop],
            [col_start, row_start],
        ]
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [coords]},
                "properties": {"change": True},
            }
        )

    return {"type": "FeatureCollection", "features": features}


def geojson_to_str(geojson: Dict[str, Any]) -> str:
    """Serialize a GeoJSON dict to a formatted string."""
    return json.dumps(geojson, indent=2)
