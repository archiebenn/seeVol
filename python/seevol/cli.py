# cli.py - command line seevol
# date: 02-11-2026
# author: Archie Benn sj19031@bristol.ac.uk (+ Claude)  

import argparse
from pathlib import Path

import numpy as np
from seevol.voxel_occlusion import visible_pairs

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute visible voxel pairs in a binary 3D .npy volume."
    )
    parser.add_argument(
        "volume",
        type=Path,
        help="input .npy volume (0 = solid, 1 = open)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="output .npz path for coords, edges, and scores",
    )
    args = parser.parse_args(argv)

    try:
        volume = np.load(args.volume, allow_pickle=False)
    except (OSError, ValueError) as error:
        parser.error(f"could not load input volume: {error}")

    if not isinstance(volume, np.ndarray):
        volume.close()
        parser.error("input must be a .npy array, not an .npz archive")
    if volume.ndim != 3:
        parser.error(f"input volume must be 3D; got {volume.ndim} dimensions")
    if volume.dtype.kind not in "biuf" or not np.isin(volume, (0, 1)).all():
        parser.error("input volume must contain only binary values 0 and 1")

    volume = np.ascontiguousarray(volume, dtype=np.uint8)
    try:
        coords, edges = visible_pairs(volume)
    except RuntimeError as error:
        parser.error(f"visibility calculation failed: {error}")

    n_open = len(coords)
    counts = np.bincount(edges.ravel(), minlength=n_open)
    scores = counts / (n_open - 1) if n_open > 1 else np.zeros(n_open)

    try:
        with args.output.open("wb") as output_file:
            np.savez(output_file, coords=coords, edges=edges, scores=scores)
    except OSError as error:
        parser.error(f"could not write output file: {error}")

    print(f"Open voxels: {n_open}")
    print(f"Visible pairs: {len(edges)}")
    print(f"Saved results to {args.output}")
    return 0