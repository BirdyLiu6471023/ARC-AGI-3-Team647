"""Frame helpers: turn raw stacked frames into arrays and stable hashes.

An ARC-AGI-3 frame response carries one or more 64x64 grid layers (each cell a
color in 0-15). These helpers give the rest of the codebase a single, stable
representation and a cheap way to detect whether the environment changed.
"""

from __future__ import annotations

import hashlib
from typing import Sequence

import numpy as np


def frames_to_array(frame: Sequence) -> np.ndarray:
    """Stack raw frame layers into a single ``(layers, H, W)`` int array.

    Accepts the ``FrameDataRaw.frame`` value, which is a list of 2D grids
    (numpy arrays or nested lists). Returns an empty array when there is no
    frame so callers can treat "no observation" uniformly.
    """
    if frame is None or len(frame) == 0:
        return np.empty((0, 0, 0), dtype=np.int16)
    layers = [np.asarray(layer, dtype=np.int16) for layer in frame]
    return np.stack(layers, axis=0)


def state_hash(grid: np.ndarray) -> str:
    """Return a stable hash of a grid array for novelty / loop detection."""
    if grid.size == 0:
        return "empty"
    return hashlib.blake2b(grid.tobytes(), digest_size=16).hexdigest()


def grid_changed(before: np.ndarray, after: np.ndarray) -> bool:
    """True if the observable grid changed between two steps."""
    if before.shape != after.shape:
        return True
    return not np.array_equal(before, after)
