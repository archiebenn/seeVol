# quickstart.py - minimal python example of seevol 
# date: 02-11-2026
# author: Archie Benn sj19031@bristol.ac.uk 

import numpy as np
import seevol 

# 1 = open, 0 = solid
volume = np.ones((3, 3, 3), dtype=np.uint8)

# adds an obstruction
volume[1, 1, 1] = 0  

# calculate pairwise voxel visibility
coords, edges = seevol.visible_pairs(volume)

print(f"{len(coords)} open voxels")
print(f"{len(edges)} visible pairs")