# example.py - imports functions to view visibility scored in 3D excavated space  
# date: 02-11-2026
# author: Archie Benn sj19031@bristol.ac.uk

import numpy as np
import seevol

# create example NumPy volume with excavator
example_nest = seevol.tunnel_excavator(size=200, seed=27, n_steps=20000, branch_prob=1e-5, radius=1)
open_coords = np.argwhere(example_nest == 1)

# view visibility scores in pyvista window
seevol.visibility_visualiser(example_nest, view_type="mip", verbose=True)

# view BFS distances from start voxel(x0,y0,z0) in pyvista window
x0,y0,z0 = open_coords[8000]
seevol.bfs_visualiser(example_nest, x0=x0, y0=y0, z0=z0)

# view shortest path from BFS algorithm between two voxels
x0,y0,z0 = open_coords[8000]
x1,y1,z1 = open_coords[30000]
seevol.bfs_shortest_path_visualiser(example_nest, x0=x0, y0=y0, z0=z0, x1=x1, y1=y1, z1=z1)

