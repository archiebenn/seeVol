# example.py - imports functions to view visibility scored in 3D excavated space  
# date: 02-11-2026
# author: Archie Benn sj19031@bristol.ac.uk

from generator import tunnel_excavator
from visualiser import visibility_visualiser 

# create example nest with excavator
example_nest = tunnel_excavator(size=150, seed=45, n_steps=15000, branch_prob=0.0001, radius=1)

# view in pyvista window
visibility_visualiser(example_nest, verbose=True)