# generate_volumes.py - generates carved volumes to simulate ant nest excavations and intricate structures
# date: 28-10-2026  
# author: Archie Benn sj19031@bristol.ac.uk 

import numpy as np
from pathlib import Path
import random
import porespy as ps

# .npy volume directory 
data_dir = Path(__file__).resolve().parent / "volumes"
data_dir.mkdir(exist_ok=True)

def tunnel_excavater(size = 100, n_steps = 20000, branch_prob = 0.02, radius = 1, seed=0):
    """
    Creates empty grid volume (default volume 100^3 voxels).

    Produces a volume with fully-connected and randomly carved tunnels within that grid volume.
    """

    rng = random.Random(seed)

    # fill size^3 volume with 0s (represents solid/non-open e.g soil within an excavated ant nest)
    vol = np.zeros((size,size,size), dtype=np.uint8)

    def excavate(position):
        """
        Takes current position and excavates by the radius provided (radius = 1 -> 3x3 excavation). 
        
        Sets 'excavated' voxel cells to 1.
        """

        # get current coordinates of 'position'
        x,y,z = position
        # define low and high positions for carving given radius
        low = [max(0, x-radius), max(0, y-radius), max(0, z-radius)]
        high = [min(size, x + radius + 1), min(size, y + radius + 1), min(size, z + radius + 1)]

        # ****actual excavation step i.e. set carved voxel(s) == 1**** 
        vol[low[0]:high[0], low[1]:high[1], low[2]:high[2]] = 1

    # begin 'excavation' with starting position near top in centre (1 down in y plane)    
    start = (size //2, size-1, size//2)
    # starting in the cebntre of the volume
    #start = (size // 2, size //2, size //2)
    excavate(start)

    # active walker list (e.g an ant excavating)
    heads = [start]
    # define how the head/ant can move (one unit in all 6 directions in this xyz space)
    #moves = [(1,0,0), (-1,0,0), # x
    #         (0,1,0), (0,-1,0), # y
    #         (0,0,1), (0,0,-1)] # z
    
    # or apply a slight y and x bias for increased chance of moving down/sideways (more ant-like)  
    # change these values in each axes to adjust excavation shapes  
    moves = (
        [(1,0,0)] * 22 + [(-1,0,0)] * 22 + # x
        [(0,1,0)] * 20 + [(0,-1,0)] * 22 + # y  
        [(0,0,1)] * 20 + [(0,0,-1)] * 20 # z
        )

    for _ in range(n_steps):

        head_idx = rng.randrange(len(heads))
        x,y,z = heads[head_idx]

        # movement selector
        dx,dy,dz = rng.choice(moves)

        # new head coordinates after move
        nx,ny,nz = x + dx, y + dy, z + dz

        # only excavates if the new coordinates are within size of voluem
        # i.e if new position does not fall outside the defined volume zone 'size'
        if 0 <= nx < size and 0 <= ny < size and 0 <= nz < size:

            # excavate and move head/ant
            excavate((nx,ny,nz))
            heads[head_idx] = (nx,ny,nz)

            # occasionally spawn new branch form current position
            if rng.random() < branch_prob:
                heads.append((nx,ny,nz))

    return vol


# tunnel network, all connected (single random-walk origin, branches only spawn from carved voxels)
# add new tunnels below, or adapt existing three 

# create volumes
a = tunnel_excavater(size=100, seed=65, n_steps=20000, branch_prob=0.0001, radius=1)
b = tunnel_excavater(size=20, seed=8, n_steps=500, branch_prob=0.0001, radius=0)
c = tunnel_excavater(size=180, seed=6, n_steps=10000, branch_prob=0.0001, radius=1)

# saving out the .npy volumes
np.save(data_dir / "nest.npy", a)
np.save(data_dir / "small_nest.npy", b)
np.save(data_dir / "large_nest.npy", c)

# some infor printed out about % of excavated volume  
print(f"nest.npy: {a.sum()} open voxels of {a.size} ({100*a.sum()/a.size:.2f}%)")
print(f"nest_small.npy: {b.sum()} open voxels of {b.size} ({100*b.sum()/b.size:.2f}%)")
print(f"nest_large.npy: {c.sum()} open voxels of {c.size} ({100*c.sum()/c.size:.2f}%)")

# some other volumes from other libraries
vol2 = ps.generators.blobs(shape=[64, 64, 64], porosity=0.5) 
np.save(data_dir /"porespy.npy", vol2.astype(np.uint8))