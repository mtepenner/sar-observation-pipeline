"""
Terrain correction module.

Flattens SAR imagery over a Digital Elevation Model (DEM) to remove
topographic distortions (foreshortening, layover, shadowing).
"""

import numpy as np


def normalize_local_incidence(
    backscatter: np.ndarray,
    dem: np.ndarray,
    sensor_incidence_angle_deg: float = 35.0,
    pixel_spacing_m: float = 10.0,
) -> np.ndarray:
    """
    Apply Range-Doppler terrain correction by normalising backscatter using
    the local incidence angle derived from the DEM.

    The local incidence angle θ_local is approximated from the DEM slope
    and the sensor look angle.  The terrain-corrected backscatter σ_tc is:

        σ_tc = σ⁰ * cos(θ_sensor) / cos(θ_local)

    Args:
        backscatter: 2-D array of calibrated backscatter values (linear scale).
        dem: 2-D array of elevation values (metres) with the same spatial
             extent and resolution as *backscatter*.
        sensor_incidence_angle_deg: Nominal sensor incidence angle in degrees.
        pixel_spacing_m: Ground-range pixel spacing in metres (used to convert
                         elevation differences to slope angles).

    Returns:
        Terrain-corrected backscatter array of the same shape.

    Raises:
        ValueError: If *backscatter* and *dem* have different shapes.
    """
    if backscatter.shape != dem.shape:
        raise ValueError(
            f"backscatter shape {backscatter.shape} does not match DEM shape {dem.shape}."
        )

    dem_f = dem.astype(np.float64)

    # Compute slope in range direction (column gradient)
    slope_rad = np.arctan(np.gradient(dem_f, pixel_spacing_m, axis=1))

    sensor_rad = np.deg2rad(sensor_incidence_angle_deg)
    local_incidence_rad = sensor_rad - slope_rad

    cos_sensor = np.cos(sensor_rad)
    cos_local = np.cos(local_incidence_rad)

    # Avoid division by near-zero cosines (shadow / layover zones)
    safe_cos_local = np.where(np.abs(cos_local) > 1e-3, cos_local, np.nan)

    corrected = backscatter.astype(np.float64) * cos_sensor / safe_cos_local
    return corrected


def terrain_flatten(
    backscatter: np.ndarray,
    dem: np.ndarray,
    sensor_incidence_angle_deg: float = 35.0,
    pixel_spacing_m: float = 10.0,
) -> np.ndarray:
    """
    Convenience wrapper around :func:`normalize_local_incidence`.

    Args:
        backscatter: Calibrated SAR backscatter (linear scale).
        dem: Co-registered DEM in metres.
        sensor_incidence_angle_deg: Nominal look angle in degrees.
        pixel_spacing_m: Pixel ground spacing in metres.

    Returns:
        Terrain-corrected backscatter array.
    """
    return normalize_local_incidence(backscatter, dem, sensor_incidence_angle_deg, pixel_spacing_m)
