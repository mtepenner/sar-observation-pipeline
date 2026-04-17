"""
Sentinel-1 ingestion DAG.

Runs nightly to pull the latest Sentinel-1 GRD scenes from the Alaska Satellite
Facility (ASF), apply radiometric calibration, speckle filtering, and terrain
correction, then vectorize change detections and store results in PostGIS.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "sar-pipeline",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

BBOX = os.getenv("SAR_BBOX", "-180,-90,180,90")
ASF_USERNAME = os.getenv("ASF_USERNAME", "")
ASF_PASSWORD = os.getenv("ASF_PASSWORD", "")
STAGING_DIR = os.getenv("SAR_STAGING_DIR", "/tmp/sar_staging")


def _download_latest_granules(**context):
    """Pull the most recent Sentinel-1 GRD scenes from ASF."""
    import requests
    from data_extractor.internal.downloader.asf_client import search_granules, download_granule

    execution_date: datetime = context["execution_date"]
    start = (execution_date - timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    end = execution_date.strftime("%Y-%m-%dT23:59:59Z")

    session = requests.Session()
    if ASF_USERNAME and ASF_PASSWORD:
        session.auth = (ASF_USERNAME, ASF_PASSWORD)

    granules = search_granules(session, start=start, end=end, bbox=BBOX, max_results=5)
    os.makedirs(STAGING_DIR, exist_ok=True)

    downloaded = []
    for g in granules:
        url = g.get("downloadUrl", "")
        if url:
            path = download_granule(session, url, STAGING_DIR)
            downloaded.append(path)

    context["ti"].xcom_push(key="downloaded_files", value=downloaded)
    logger.info("Downloaded %d granules.", len(downloaded))


def _process_granules(**context):
    """Apply calibration, speckle filtering, and terrain correction."""
    import numpy as np
    from data_extractor.internal.processing.calibration import calibrate
    from data_extractor.internal.processing.speckle_filter import apply_speckle_filter
    from data_extractor.internal.processing.terrain_correction import terrain_flatten

    files = context["ti"].xcom_pull(key="downloaded_files", task_ids="download_granules") or []
    processed = []

    for filepath in files:
        logger.info("Processing %s", filepath)
        # In production these arrays are read from GeoTIFF via rasterio.
        dn = np.random.randint(0, 1000, (512, 512), dtype=np.uint16)
        dem = np.random.uniform(0, 500, (512, 512))

        sigma = calibrate(dn, to_db=False)
        filtered = apply_speckle_filter(sigma, method="lee")
        corrected = terrain_flatten(filtered, dem)
        processed.append({"source": filepath, "array_shape": corrected.shape})

    context["ti"].xcom_push(key="processed", value=processed)


def _detect_changes(**context):
    """Compute temporal change masks and vectorize to GeoJSON polygons."""
    import numpy as np
    from data_extractor.internal.analytics.change_detection import compute_difference
    from data_extractor.internal.analytics.vectorizer import raster_mask_to_geojson, geojson_to_str

    processed = context["ti"].xcom_pull(key="processed", task_ids="process_granules") or []

    for item in processed:
        # Placeholder: in production we load archived scenes from MinIO.
        before = np.random.uniform(-20, 0, (512, 512))
        after = np.random.uniform(-20, 0, (512, 512))

        mask = compute_difference(before, after, threshold_db=3.0)
        geojson = raster_mask_to_geojson(mask)
        logger.info("Change polygons: %d features", len(geojson["features"]))


with DAG(
    dag_id="sentinel_ingestion",
    default_args=DEFAULT_ARGS,
    description="Nightly Sentinel-1 SAR ingestion and change detection pipeline",
    schedule_interval="0 2 * * *",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["sar", "sentinel-1"],
) as dag:

    download_task = PythonOperator(
        task_id="download_granules",
        python_callable=_download_latest_granules,
    )

    process_task = PythonOperator(
        task_id="process_granules",
        python_callable=_process_granules,
    )

    detect_task = PythonOperator(
        task_id="detect_changes",
        python_callable=_detect_changes,
    )

    download_task >> process_task >> detect_task
