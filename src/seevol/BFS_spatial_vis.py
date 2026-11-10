# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# BFS_spatial_vis.py - Pyvista visualisations for BFS-based spatial analyses of binary 3D volumes

import numpy as np
import pyvista as pv
import seevol


def bfs_all_vis(vol, x0, y0, z0):
    """
    Takes a volume in .npy format with binary voxel values of 0 or 1 (0 = empty, 1 = solid), and coordinates of a starting voxel in this volume.

    Runs the bfs_distances function (written in C++ for efficiency) to compute distanc scores for every open voxel in the volume.

    Distance scores of open voxels are then visualised in 3D on the volume using pyvista.
    """

    # run main BFS algorithm
    coords, distances = seevol.bfs_distances(vol, x0, y0, z0)

    # now gamma compress the distances so low/high aren't as far visually
    # as long as not unreachable/-1 due to power error
    mask = distances != -1
    distances[mask] = distances[mask] ** 0.5

    # create 3D grid with dimensions defined by .npy volume size (+ 1 cell in each dimension for pyvista)
    p = pv.Plotter()
    grid = pv.ImageData(dimensions=np.array(vol.shape) + 1)

    # flatten cells for pyvista (Fortran F) and mark empty voxels
    grid.cell_data["open"] = (vol == 0).flatten(order="F")
    distance_volume = np.zeros(vol.shape, dtype=np.float32, order="F")
    distance_volume[tuple(coords.T)] = distances

    # apply distance scores from BFS to each voxel
    grid.cell_data["bfs_distance"] = distance_volume.ravel(order="F")
    grid = grid.cell_data_to_point_data()

    # add mesh for full volume outline in black (wire frame)
    p.add_mesh(grid.outline(), color="black", line_width=1.25)
    p.add_axes(viewport=(0, 0, 0.2, 0.2))

    # add voxels to volume coloured by BFS distances from starting voxel
    p.add_volume(
        grid,
        scalars="bfs_distance",
        cmap="YlGn",
        blending="maximum",
        shade=False,
        opacity="linear",
    )

    # also add faint wireframe mesh around all open voxels fdor clarity
    open_mesh = grid.threshold(0.5, scalars="open")
    p.add_mesh(
        open_mesh,
        color="grey",
        style="wireframe",
        opacity=0.1,
        line_width=1,
    )

    # mark start voxel
    # T0D0: fix this as it is not marking start voxel
    p.add_points(np.array([coords[0]], dtype=float), color="red", point_size=16)
    p.add_text(
        f"BFS path lengths to all open voxels from start voxel {int(x0), int(y0), int(z0)}",
        font_size=12,
    )
    p.camera_position = "zy"
    p.show()


def bfs_shortest_vis(vol, x0, y0, z0, x1, y1, z1):
    """
    Takes a volume in .npy format with binary voxel values of 0 or 1 (0 = empty, 1 = solid), and coordinates of a start and end voxel.

    Runs the shortest_path_bfs function (written in C++ for efficiency) to compute the shortest open-voxel path between them using BFS algorithm.

    Draws the full volume outline + open voxel wireframe in pyvista, with the shortest path overlaid as a line.
    """

    # run C++ shortest path BFS algorithm
    path_coords, distance = seevol.shortest_path_bfs(vol, x0, y0, z0, x1, y1, z1)

    # create 3D grid with dimensions defined by .npy volume size (+1 cell in each dimension for pyvista)
    p = pv.Plotter()
    grid = pv.ImageData(dimensions=np.array(vol.shape) + 1)

    # flatten cells for pyvista (Fortran order) and mark empty voxels
    grid.cell_data["open"] = (vol == 0).flatten(order="F")
    grid = grid.cell_data_to_point_data()

    # add mesh for full volume outline in black (wireframe)
    p.add_mesh(grid.outline(), color="black", line_width=1.25)
    p.add_axes(viewport=(0, 0, 0.2, 0.2))

    # add wireframe mesh around all open voxels for context
    open_mesh = grid.threshold(0.5, scalars="open")
    p.add_mesh(
        open_mesh,
        color="grey",
        style="wireframe",
        opacity=0.1,
        line_width=1,
    )

    # draw shortest path as a red line through voxel-centre coordinates
    # simple transformation from C++ output of coordinates
    line = pv.lines_from_points(path_coords.astype(float))
    p.add_mesh(line, color="red", line_width=4)

    # mark start/end voxels
    p.add_points(np.array([path_coords[0]], dtype=float), color="green", point_size=16)
    p.add_points(
        np.array([path_coords[-1]], dtype=float), color="orange", point_size=16
    )

    p.add_text(
        f"BFS path length from {int(x0), int(y0), int(z0)} (green) to {int(x1), int(y1), int(z1)} (orange)\nPath length: {distance} voxel units",
        font_size=12,
    )
    p.camera_position = "zy"
    p.show()
