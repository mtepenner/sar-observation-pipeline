"""
Change detection module.

Computes temporal differences between two SAR passes to identify
surface-change events such as deforestation or ice-shelf collapse.
"""

import numpy as np


def compute_difference(
    image_before: np.ndarray,
    image_after: np.ndarray,
    threshold_db: float = 3.0,
) -> np.ndarray:
    """
    Compute the pixel-wise difference between two SAR backscatter images
    (both in dB scale) and return a binary change mask.

    A pixel is flagged as *changed* when:
        |σ_after - σ_before| > threshold_db

    Args:
        image_before: 2-D array of pre-event backscatter values (dB).
        image_after: 2-D array of post-event backscatter values (dB).
        threshold_db: Absolute dB change required to classify a pixel as changed.

    Returns:
        Boolean array with True where significant change was detected.

    Raises:
        ValueError: If the arrays have different shapes or threshold_db <= 0.
    """
    if image_before.shape != image_after.shape:
        raise ValueError(
            f"Shape mismatch: before={image_before.shape}, after={image_after.shape}."
        )
    if threshold_db <= 0:
        raise ValueError("threshold_db must be a positive number.")

    diff = image_after.astype(np.float64) - image_before.astype(np.float64)
    change_mask = np.abs(diff) > threshold_db
    return change_mask


def compute_ratio(
    image_before: np.ndarray,
    image_after: np.ndarray,
    threshold: float = 2.0,
) -> np.ndarray:
    """
    Compute the log-ratio between two SAR images in linear scale and return
    a binary change mask.

    Log-ratio: R = |log(σ_after / σ_before)|

    Args:
        image_before: Pre-event backscatter (linear scale, > 0).
        image_after: Post-event backscatter (linear scale, > 0).
        threshold: Log-ratio threshold for change classification.

    Returns:
        Boolean array with True where |log-ratio| > threshold.

    Raises:
        ValueError: If arrays have different shapes or threshold <= 0.
    """
    if image_before.shape != image_after.shape:
        raise ValueError(
            f"Shape mismatch: before={image_before.shape}, after={image_after.shape}."
        )
    if threshold <= 0:
        raise ValueError("threshold must be a positive number.")

    before = np.where(image_before > 0, image_before, np.nan).astype(np.float64)
    after = np.where(image_after > 0, image_after, np.nan).astype(np.float64)

    log_ratio = np.abs(np.log(after / before))
    change_mask = log_ratio > threshold
    return change_mask


def mask_to_labeled_regions(change_mask: np.ndarray) -> np.ndarray:
    """
    Label connected components in a binary change mask.

    Args:
        change_mask: Boolean 2-D array.

    Returns:
        Integer array where each connected changed region has a unique label > 0.
    """
    from scipy.ndimage import label as nd_label

    labeled, _ = nd_label(change_mask)
    return labeled
