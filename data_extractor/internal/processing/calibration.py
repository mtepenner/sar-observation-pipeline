"""
Radiometric calibration module.

Translates raw Sentinel-1 digital numbers (DN) to radar backscatter (sigma-naught)
using the standard SNAP/ESA calibration formula.
"""

import numpy as np


def dn_to_sigma_naught(dn: np.ndarray, calibration_constant: float = 1.0) -> np.ndarray:
    """
    Convert digital number (DN) values to sigma-naught (σ⁰) in linear power units.

    Formula: σ⁰ = DN² / calibration_constant

    Args:
        dn: Array of raw digital number values.
        calibration_constant: Calibration constant from the Sentinel-1 annotation XML.

    Returns:
        Array of sigma-naught values in linear scale.
    """
    if calibration_constant <= 0:
        raise ValueError("calibration_constant must be a positive number.")
    sigma = (dn.astype(np.float64) ** 2) / calibration_constant
    return sigma


def sigma_naught_to_db(sigma: np.ndarray) -> np.ndarray:
    """
    Convert sigma-naught from linear scale to decibel (dB) scale.

    Args:
        sigma: Array of sigma-naught values in linear scale.

    Returns:
        Array of sigma-naught values in dB.
    """
    sigma = np.where(sigma > 0, sigma, np.nan)
    return 10.0 * np.log10(sigma)


def calibrate(dn: np.ndarray, calibration_constant: float = 1.0, to_db: bool = True) -> np.ndarray:
    """
    Full calibration pipeline: DN → sigma-naught (optionally in dB).

    Args:
        dn: Raw digital number array.
        calibration_constant: Calibration constant from metadata.
        to_db: If True, output is in dB scale; otherwise linear.

    Returns:
        Calibrated backscatter array.
    """
    sigma = dn_to_sigma_naught(dn, calibration_constant)
    if to_db:
        return sigma_naught_to_db(sigma)
    return sigma
