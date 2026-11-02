# pyvista_example.py - view pyvista example outputs coloured buy voxel visibility scores 
# date: 28-10-2026
# author: Archie Benn sj19031@bristol.ac.uk 

import numpy as np
import time
import pyvista as pv
from pathlib import Path
from visivox.ray_occlusion_cpp import visible_pairs

# get data directory  
data_dir = Path(__file__).resolve().parent / "volumes"

# load in generated example nest volume .npys
small_nest = np.load(data_dir / "small_nest.npy")
medium_nest = np.load(data_dir / "nest.npy")
large_nest = np.load(data_dir / "large_nest.npy")
porespy = np.load(data_dir / "porespy.npy")


def visibility_visualiser(vol):
    """
    Takes a volume in .npy format with binary voxel values of 0 or 1 (0 = solid, 1 = open).  

    Runs the visible_pairs function (written in C++ for efficiency) and computes visibility scores for every open voxel in the volume.

    Visibility scores of open voxels are then visualised in 3D on the volume using pyvista.
    """

    t0_build = time.perf_counter()

    # run main C++ Amanatides & Woo algorithm for ray tracing and visibility checking all open voxel pairs  
    t0_cpp = time.perf_counter()
    coords, edges = visible_pairs(vol)
    t_cpp = time.perf_counter() - t0_cpp

    n = len(coords)
    n_rays = n * (n - 1) // 2

    # count visible connections per voxel (each edge contributes to both endpoints)
    # gives a 'visibility score' to each voxel based on visible counts to other voxels  
    counts = np.bincount(edges[:, 0], minlength=n) + np.bincount(edges[:, 1], minlength=n)
    scores = counts / (n - 1)  # normalises if un-hashed

    # create 3D grid with dimensions defined by .npy volume size (+ 1 cell in each dimension for pyvista)
    p = pv.Plotter()
    #p.enable_depth_peeling(number_of_peels=100, occlusion_ratio=0.0)
    grid = pv.ImageData(dimensions=np.array(vol.shape) + 1)

    # flatten cells for pyvista and set every cell/voxel to 0  
    grid.cell_data["open"] = vol.flatten(order="F")
    score_volume = np.zeros(vol.shape, dtype=float) 

    # apply visibility scores to the cell/voxel in volume
    score_volume[tuple(coords.T)] = scores
    grid.cell_data["visibility_score"] = score_volume.flatten(order="F")
    grid = grid.cell_data_to_point_data() 

    # transparent outline of the full volume bounds for spatial context  
    p.add_mesh(grid.outline(), color="black", line_width=1.25)

    # render the visibility volume with MIP style ray-casting (takes max. voxel value per 'viewing ray' in pyvista)  
    p.add_volume(
            grid,
            scalars="visibility_score",
            cmap="turbo",
            blending="maximum",
            shade=False,
            opacity="linear",
    )

    # add an open mesh around each of the 1s to highlight the full excavated volume more clearly
    open_mesh = grid.threshold(0.5, scalars="open")
    p.add_mesh(
            open_mesh,
            color="grey",
            style="wireframe",
            opacity=0.1,
            line_width=1,
    )
    
    # un-comment to have an interactive plane-slider within the volume   
    # p.add_mesh_clip_plane(voxel_mesh, scalars="visibility_score", cmap="turbo")

    t_build = time.perf_counter() - t0_build

    print(f"Open voxels: {n}, rays cast: {n_rays:,}, visible pairs: {len(edges):,}")
    print(f"Time in C++ 'hot loop': {t_cpp:.5f}s")
    print(f"Average time per ray: {t_cpp / n_rays * 1e6:.5f} µs")
    print(f"Total time before render: {t_build:.3f}s")

    # show pyvista render in window
    p.camera_position = 'zy'
    p.show()


visibility_visualiser(large_nest)
