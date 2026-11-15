# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# pyvista_surfaces.py - Uses Pyvista to extract surface meshes from voxelised volumes  
# UNFINISHED as of 15-11-26  

import numpy as np
import pyvista as pv
import seevol

# create example NumPy volume with excavate_tunnels() function
#example_nest = seevol.excavate_tunnels(
#    size=100, seed=78, n_steps=30000, branch_prob=1e-5, radius=1
#)

def extract_surfaces(vol):

    # create 3D grid with dimensions defined by .npy volume size (+ 1 cell in each dimension for pyvista)
    grid = pv.ImageData(dimensions=np.array(vol.shape) + 1)
    grid = grid.cell_data_to_point_data()

    # flatten cells for pyvista (Fortran F) and mark empty voxels
    grid.cell_data["open"] = (vol == 0).flatten(order="F")

    # label_ids = np.unique(grid.active_scalars) - active scalars are just 0/1 or False/True

    # function copied from: https://docs.pyvista.org/api/core/_autosummary/pyvista.imagedatafilters.contour_labels
    def labels_plotter(mesh, zoom=None):
        colored_mesh = mesh.color_labels(negative_indexing=True)
        pl = pv.Plotter()
        pl.add_mesh(colored_mesh, show_edges=True)
        if zoom:
            pl.camera.zoom(zoom)
        return pl

    # extracts the surface and shows
    contours = grid.contour_labels()

    # plotter
    p = labels_plotter(contours)
    # add mesh for full volume outline in black (wireframe)
    p.add_mesh(grid.outline(), color="black", line_width=1.25)
    p.add_axes(viewport=(0, 0, 0.2, 0.2))
    p.camera_position = "zy"
    p.show()

#extract_surfaces(example_nest)