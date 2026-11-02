# example.py - imports functions to view visibility scored in 3D excavated space  
# date: 02-11-2026
# author: Archie Benn sj19031@bristol.ac.uk

import seevol

# create example NumPy volume with excavator
example_nest = seevol.tunnel_excavator(size=180, seed=14, n_steps=18000, branch_prob=1e-5, radius=1)

# view visibility in pyvista window
seevol.visibility_visualiser(example_nest, verbose=True)