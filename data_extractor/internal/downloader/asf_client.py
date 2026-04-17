"""
ASF (Alaska Satellite Facility) client module.

Provides utilities to search for and download Sentinel-1 GRD/SLC scenes
from the ASF Search API (https://search.asf.alaska.edu/).
"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

ASF_SEARCH_URL = "https://api.daac.asf.alaska.edu/services/search/param"


def build_search_params(
    platform: str = "Sentinel-1",
    product_type: str = "GRD_HD",
    start: Optional[str] = None,
    end: Optional[str] = None,
    bbox: Optional[str] = None,
    max_results: int = 10,
) -> Dict[str, Any]:
    """
    Build a query parameter dict for the ASF granule search endpoint.

    Args:
        platform: Satellite platform name (e.g. 'Sentinel-1').
        product_type: Product type ('GRD_HD', 'SLC', etc.).
        start: ISO-8601 start date string (e.g. '2024-01-01T00:00:00Z').
        end: ISO-8601 end date string.
        bbox: Bounding box string 'west,south,east,north' in WGS-84 degrees.
        max_results: Maximum number of results to return.

    Returns:
        Dictionary of query parameters.
    """
    params: Dict[str, Any] = {
        "platform": platform,
        "processingLevel": product_type,
        "maxResults": max_results,
        "output": "json",
    }
    if start:
        params["start"] = start
    if end:
        params["end"] = end
    if bbox:
        params["bbox"] = bbox
    return params


def search_granules(
    session,
    platform: str = "Sentinel-1",
    product_type: str = "GRD_HD",
    start: Optional[str] = None,
    end: Optional[str] = None,
    bbox: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """
    Search ASF for Sentinel-1 granules matching the given criteria.

    Args:
        session: A requests.Session (or compatible) object with valid ASF credentials.
        platform: Satellite platform.
        product_type: Product type.
        start: Start date (ISO-8601).
        end: End date (ISO-8601).
        bbox: Bounding box string 'west,south,east,north'.
        max_results: Upper bound on returned results.

    Returns:
        List of granule metadata dicts.
    """
    params = build_search_params(platform, product_type, start, end, bbox, max_results)
    response = session.get(ASF_SEARCH_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    results = data[0] if data else []
    logger.info("ASF search returned %d granules.", len(results))
    return results


def download_granule(
    session,
    download_url: str,
    dest_dir: str,
) -> str:
    """
    Download a single granule zip archive from ASF.

    Args:
        session: Authenticated requests.Session.
        download_url: Direct download URL from the granule metadata.
        dest_dir: Local directory where the file will be saved.

    Returns:
        Absolute path to the downloaded file.
    """
    filename = os.path.basename(download_url.split("?")[0])
    dest_path = os.path.join(dest_dir, filename)

    logger.info("Downloading %s → %s", download_url, dest_path)
    with session.get(download_url, stream=True, timeout=120) as resp:
        resp.raise_for_status()
        with open(dest_path, "wb") as fh:
            for chunk in resp.iter_content(chunk_size=8192):
                fh.write(chunk)

    logger.info("Download complete: %s", dest_path)
    return dest_path
