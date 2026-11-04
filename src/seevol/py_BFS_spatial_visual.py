# py_BFS_spatial_visual.py - view pyvista outputs coloured by BFS spatial scores 
# date: 04-11-2026
# author: Archie Benn sj19031@bristol.ac.uk 

import numpy as np
import pyvista as pv
import seevol

def spatial_visualiser(vol, x0, y0, z0):
    """
        Takes a volume in .npy format with binary voxel values of 0 or 1 (0 = solid, 1 = open), and coordinates of a starting voxel in this volume.  
    
        Runs the bfs_distances function (written in C++ for efficiency) to compute distanc scores for every open voxel in the volume.
    
        Distance scores of open voxels are then visualised in 3D on the volume using pyvista.
        """

    # run main BFS algorithm  
    coords, distances = seevol.bfs_distances(vol, x0, y0, z0)

    # create 3D grid with dimensions defined by .npy volume size (+ 1 cell in each dimension for pyvista)
    p = pv.Plotter()
    grid = pv.ImageData(dimensions=np.array(vol.shape) + 1)

    # flatten cells for pyvista (Fortran F) and set every cell/voxel to 0
    grid.cell_data["open"] = vol.flatten(order="F")
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
        cmap="YlGnBu",
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

    p.camera_position = "zy"
    p.show()