# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# visualiser_example.py - Runs example seeVol visualisations for binary 3D volumes  

import numpy as np
import seevol

# create example NumPy volume with excavator
example_nest = seevol.tunnel_excavator(size=200, seed=27, n_steps=20000, branch_prob=1e-5, radius=1)
open_coords = np.argwhere(example_nest == 0)

# view visibility scores in pyvista window
seevol.visibility_vis(example_nest, view_type="mip", verbose=True)

# view BFS distances from start voxel(x0,y0,z0) in pyvista window
x0,y0,z0 = open_coords[100]
seevol.bfs_all_vis(example_nest, x0=x0, y0=y0, z0=z0)

# view shortest path from BFS algorithm between two voxels
x0,y0,z0 = open_coords[100]
x1,y1,z1 = open_coords[1600]
seevol.bfs_shortest_vis(example_nest, x0=x0, y0=y0, z0=z0, x1=x1, y1=y1, z1=z1)
