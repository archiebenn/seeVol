# example.py - imports functions to view visibility scored in 3D excavated space  
# date: 02-11-2026
# author: Archie Benn sj19031@bristol.ac.uk

import numpy as np
import seevol

# create example NumPy volume with excavator
example_nest = seevol.tunnel_excavator(size=200, seed=14, n_steps=40000, branch_prob=1e-5, radius=1)

# view visibility in pyvista window
seevol.visibility_visualiser(example_nest, view_type="mip", verbose=True)

# view distances from start voxel(x0,y0,z0) in pyvista window
open_coords = np.argwhere(example_nest == 1)
x,y,z = open_coords[100]
assert(example_nest[x, y, z]) == 1
seevol.spatial_visualiser(example_nest, x0=x, y0=y, z0=z)