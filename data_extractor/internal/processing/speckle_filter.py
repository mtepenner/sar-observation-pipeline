"""
Speckle filter module.

Applies Lee or Frost filters to SAR imagery to reduce multiplicative speckle noise
while preserving edge detail.
"""

import numpy as np
from scipy.ndimage import uniform_filter


def lee_filter(image: np.ndarray, window_size: int = 7) -> np.ndarray:
    """
    Apply the Lee speckle filter to a SAR image.

    The Lee filter is an adaptive filter that smooths homogeneous regions while
    preserving edges by weighting based on local statistics.

    Args:
        image: 2-D numpy array of SAR backscatter values.
        window_size: Side length of the square sliding window (must be odd).

    Returns:
        Filtered image array of the same shape.

    Raises:
        ValueError: If window_size is not a positive odd integer.
    """
    if window_size < 1 or window_size % 2 == 0:
        raise ValueError("window_size must be a positive odd integer.")

    img = image.astype(np.float64)

    local_mean = uniform_filter(img, size=window_size)
    local_mean_sq = uniform_filter(img ** 2, size=window_size)

    local_var = local_mean_sq - local_mean ** 2
    local_var = np.maximum(local_var, 0.0)

    # Equivalent number of looks (ENL) estimation using image-level statistics
    overall_mean = np.nanmean(img)
    overall_var = np.nanvar(img)
    noise_var = (overall_var / (overall_mean ** 2)) if overall_mean != 0 else 1.0

    weight = local_var / (local_var + noise_var * local_mean ** 2 + 1e-10)
    filtered = local_mean + weight * (img - local_mean)
    return filtered


def frost_filter(image: np.ndarray, window_size: int = 7, damping_factor: float = 2.0) -> np.ndarray:
    """
    Apply the Frost speckle filter to a SAR image.

    The Frost filter uses an exponential damping function based on local coefficient
    of variation to adaptively weight neighbouring pixels.

    Args:
        image: 2-D numpy array of SAR backscatter values.
        window_size: Side length of the square sliding window (must be odd).
        damping_factor: Controls the degree of smoothing. Higher values increase
                        smoothing in homogeneous regions.

    Returns:
        Filtered image array of the same shape.

    Raises:
        ValueError: If window_size is not a positive odd integer or damping_factor <= 0.
    """
    if window_size < 1 or window_size % 2 == 0:
        raise ValueError("window_size must be a positive odd integer.")
    if damping_factor <= 0:
        raise ValueError("damping_factor must be positive.")

    img = image.astype(np.float64)
    half = window_size // 2
    rows, cols = img.shape
    result = np.zeros_like(img)

    for r in range(rows):
        for c in range(cols):
            r_min = max(0, r - half)
            r_max = min(rows, r + half + 1)
            c_min = max(0, c - half)
            c_max = min(cols, c + half + 1)
            patch = img[r_min:r_max, c_min:c_max]

            local_mean = np.mean(patch)
            local_std = np.std(patch)
            cv = local_std / (local_mean + 1e-10)

            # Build distance weights
            pr, pc = np.mgrid[r_min:r_max, c_min:c_max]
            dist = np.sqrt((pr - r) ** 2 + (pc - c) ** 2)
            weights = np.exp(-damping_factor * cv * dist)
            result[r, c] = np.sum(weights * patch) / (np.sum(weights) + 1e-10)

    return result


def apply_speckle_filter(
    image: np.ndarray,
    method: str = "lee",
    window_size: int = 7,
    damping_factor: float = 2.0,
) -> np.ndarray:
    """
    Apply a named speckle filter to a SAR image.

    Args:
        image: 2-D numpy array of SAR backscatter values.
        method: Filter algorithm to use – 'lee' or 'frost'.
        window_size: Sliding window size (odd integer).
        damping_factor: Damping factor used only by the Frost filter.

    Returns:
        Filtered image array.

    Raises:
        ValueError: If an unsupported method is specified.
    """
    method = method.lower()
    if method == "lee":
        return lee_filter(image, window_size)
    elif method == "frost":
        return frost_filter(image, window_size, damping_factor)
    else:
        raise ValueError(f"Unsupported speckle filter method: '{method}'. Choose 'lee' or 'frost'.")
