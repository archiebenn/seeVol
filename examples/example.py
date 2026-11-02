# example.py - imports functions to view visibility scored in 3D excavated space  
# date: 02-11-2026
# author: Archie Benn sj19031@bristol.ac.uk

import seevol

# create example NumPy volume with excavator
example_nest = seevol.tunnel_excavator(size=150, seed=9, n_steps=20000, branch_prob=0.0001, radius=1)

# view visibility in pyvista window
seevol.visibility_visualiser(example_nest, verbose=True)