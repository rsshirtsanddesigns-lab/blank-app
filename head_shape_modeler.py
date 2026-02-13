from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

import cv2
import numpy as np


@dataclass
class ShapeExtractionResult:
    normalized_mask: np.ndarray
    normalized_contour: np.ndarray
    original_mask: np.ndarray


def _largest_contour(binary_mask: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No visible shape was found. Try increasing contrast or changing threshold mode.")
    return max(contours, key=cv2.contourArea)


def extract_head_shape(
    image_bgr: np.ndarray,
    canvas_size: int = 512,
    threshold_mode: str = "auto",
    invert: bool = False,
    min_area_ratio: float = 0.01,
) -> ShapeExtractionResult:
    """Extract and normalize a silhouette/head contour from an image."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    if threshold_mode == "auto":
        _, mask = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif threshold_mode == "adaptive":
        mask = cv2.adaptiveThreshold(
            blur,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            2,
        )
    else:
        raise ValueError("threshold_mode must be 'auto' or 'adaptive'.")

    if invert:
        mask = cv2.bitwise_not(mask)

    kernel = np.ones((5, 5), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contour = _largest_contour(mask)
    area = cv2.contourArea(contour)
    if area < min_area_ratio * (mask.shape[0] * mask.shape[1]):
        raise ValueError("Detected contour is too small. Crop tighter around the head/silhouette.")

    x, y, w, h = cv2.boundingRect(contour)
    cropped_mask = mask[y : y + h, x : x + w]

    normalized = np.zeros((canvas_size, canvas_size), dtype=np.uint8)
    scale = min((canvas_size * 0.85) / w, (canvas_size * 0.85) / h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    resized = cv2.resize(cropped_mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)

    x0 = (canvas_size - new_w) // 2
    y0 = (canvas_size - new_h) // 2
    normalized[y0 : y0 + new_h, x0 : x0 + new_w] = resized

    normalized_contour = _largest_contour(normalized)

    return ShapeExtractionResult(
        normalized_mask=normalized,
        normalized_contour=normalized_contour,
        original_mask=mask,
    )


def combine_shapes(masks: Iterable[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """Average multiple normalized masks into one consensus shape and contour."""
    mask_list: List[np.ndarray] = [m.astype(np.float32) / 255.0 for m in masks]
    if not mask_list:
        raise ValueError("No masks were provided for combination.")

    mean_mask = np.mean(np.stack(mask_list, axis=0), axis=0)
    consensus = (mean_mask >= 0.5).astype(np.uint8) * 255

    kernel = np.ones((3, 3), dtype=np.uint8)
    consensus = cv2.morphologyEx(consensus, cv2.MORPH_CLOSE, kernel)
    contour = _largest_contour(consensus)

    return consensus, contour


def contour_to_overlay(base_mask: np.ndarray, contour: np.ndarray, color: Tuple[int, int, int]) -> np.ndarray:
    """Create a color image overlay with contour drawn on top of a mask."""
    base_rgb = cv2.cvtColor(base_mask, cv2.COLOR_GRAY2RGB)
    cv2.drawContours(base_rgb, [contour], -1, color, 2)
    return base_rgb
