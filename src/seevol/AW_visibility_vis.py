# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# AW_visibility_vis.py - Pyvista visualisations for A&W-based visibility analyses of binary 3D volumes

import numpy as np
import time
import pyvista as pv
import seevol


def visibility_vis(vol, view_type="mip", verbose=False):
    """
    Takes a volume in .npy format with binary voxel values of 0 or 1 (0 = empty, 1 = solid).

    Runs the visibility_scores function (written in C++ for efficiency) to compute visibility scores for every open/empty voxel in the volume.

    Visibility scores of open voxels are then visualised in 3D on the volume using pyvista.
    """

    t0_build = time.perf_counter()

    if verbose == True:
        # (same as n below)
        n_open = np.count_nonzero(vol == 0)
        print(
            f"Volume information: {n_open} open voxels of {vol.size} ({100 * n_open / vol.size:.2f}%)"
        )

    # run main C++ Amanatides & Woo algorithm for ray tracing and visibility checking all open voxel pairs
    t0_cpp = time.perf_counter()
    if verbose == True:
        coords, counts = seevol.visibility_scores(vol, verbose=True)
    else:
        coords, counts = seevol.visibility_scores(vol)
    t_cpp = time.perf_counter() - t0_cpp

    n = len(coords)
    n_rays = n * (n - 1) // 2
    scores = counts / (n - 1)  # normalises if un-hashed
    # now gamma compress the scores so low/high aren't as far visually
    scores = scores**0.4

    # create 3D grid with dimensions defined by .npy volume size (+ 1 cell in each dimension for pyvista)
    p = pv.Plotter()
    grid = pv.ImageData(dimensions=np.array(vol.shape) + 1)

    # flatten cells for pyvista (Fortran F) and mark empty voxels
    grid.cell_data["open"] = (vol == 0).flatten(order="F")
    # float32 uses 1/2 memory to default float64
    score_volume = np.zeros(vol.shape, dtype=np.float32, order="F")

    # apply visibility scores to the cell/voxel in volume
    # coords.T = transposed numpy array (flip along diagonal)
    print(coords.shape)  # (n,3) = n arrays of length 3
    print(
        coords.T.shape
    )  # (3,n) - better as 3 arrays of length n and numpy expects this
    score_volume[tuple(coords.T)] = scores

    # .ravel stops duplicate with .flatten as previously done
    grid.cell_data["voxel_visibility_score"] = score_volume.ravel(order="F")
    grid = grid.cell_data_to_point_data()

    # transparent outline of the full volume bounds for spatial context
    p.add_mesh(grid.outline(), color="black", line_width=1.25)

    # add axes arrows
    viewport = (0, 0, 0.2, 0.2)
    p.add_axes(viewport=viewport)

    # default maximum intensity projection (MIP) style ray-casting (max voxel value per ray from viewpoint)
    if view_type == "mip":
        p.add_volume(
            grid,
            scalars="voxel_visibility_score",
            cmap="turbo",
            blending="maximum",
            shade=False,
            opacity="linear",
        )

        # add an open mesh to highlight the full excavated volume more clearly
        open_mesh = grid.threshold(0.5, scalars="open")
        p.add_mesh(
            open_mesh,
            color="grey",
            style="wireframe",
            opacity=0.1,
            line_width=1,
        )

    # with interactive plane-slicer only render visibility at the plane slice
    elif view_type == "slices":
        # add plane slider
        p.add_mesh_clip_plane(grid, scalars="voxel_visibility_score", cmap="turbo")

        # add an open mesh to highlight the full excavated volume more clearly
        open_mesh = grid.threshold(0.5, scalars="open")
        p.add_mesh(
            open_mesh,
            color="grey",
            style="wireframe",
            opacity=0.1,
            line_width=1,
        )

    else:
        print(
            "Please select a valid view type for this pyvista render (see docs for more information)"
        )

    t_build = time.perf_counter() - t0_build

    if verbose == True:
        n_pairs = int(counts.sum()) // 2
        print(f"Open voxels: {n}, rays cast: {n_rays:,}, visible pairs: {n_pairs:,}")
        print(f"Time in C++ 'hot loop': {t_cpp:.5f}s")
        print(f"Average time per ray: {t_cpp / n_rays * 1e6:.5f} µs")
        print(f"Total time before render: {t_build:.3f}s")

    # show pyvista render in window
    p.add_text(
        f"Visibility scores for every open voxel in the volume from ray tracing",
        font_size=12,
    )
    p.camera_position = "zy"
    p.show()
