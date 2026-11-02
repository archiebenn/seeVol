# seeVol

`seevol` is a tool for 3D binary volumes (0 = solid, 1 = open) stored as NumPy arrays. The core functionality is based on the Amanatides & Woo voxel traversal algorithm (1), and implemented in C++ to compute straight line visibility between all pairs of open voxels in a provided volume.  

The main function `visible_pairs()` outputs two NumPy arrays: one containing the open voxel coordinates within the volume (coords: N, 3) and another with visible pair indices (edges: M, 2) which refer to rows in coords. (For example, if `edges[0]` is `[2, 7]`, the visibility edge connects `coords[2]` and `coords[7]` and these two voxels are visible to each other).  

Downstream analyses or visualisations are then possible from this output, such as visualising a 'visibility heatmap' using `pyvista` (see below)  

## Dependencies

A C++ build toolchain is required for source installation (C++17 or above)  

## Installation

To install `seevol`, run:  

```
pip install seevol
```

or for `uv` users:

```
uv pip install seevol
```

## Limitations  

This tool currently uses all-pair calculation using voxel ray traversal. Because of this, the ray traversal algorithm scales with O(open_voxels^2), and is therefore quickly unusable for large volumes.  

A hard limit is imposed in the C++ source file which limits open voxels to 1,000,000. In reality, over 500,000 open voxels will likely cause a slowdown as this runs on CPU, and methods to reduce this runtime will hopefully be introduced over time.

## Minimal example

The [quickstart example](examples/quickstart.py) creates a small volume of open voxels with one solid voxel blocking visibility:

```python
import numpy as np
from seevol.voxel_occlusion import visible_pairs

# 1 = open, 0 = solid
volume = np.ones((3, 3, 3), dtype=np.uint8)
# adds an obstruction
volume[1, 1, 1] = 0

coords, edges = visible_pairs(volume)

print(f"{len(coords)} open voxels")
print(f"{len(edges)} visible pairs")
```

It prints the number of open voxels and visible pairs:

```
26 open voxels
214 visible pairs
```

## Visualisation example on a large volume

![150_cubed](https://github.com/archiebenn/wise-pears/blob/main/images/realistic_nest.png "150^3 ant excavation example volume")

## Command-line usage

The `seevol` command analyses a 3D binary volume saved as a `.npy` file:

```bash
seevol binary_volume.npy --output visibility.npz
```

The output archive contains:

- `coords`: an `(N, 3)` array of open voxel coordinates.
- `edges`: an `(M, 2)` array of visible-pair indices into `coords`.
- `scores`: a length-`N` array with each voxel's visible-pair count divided by `N - 1` (zero when fewer than two voxels are open).

Load the results in Python with `np.load("visibility.npz")`.
