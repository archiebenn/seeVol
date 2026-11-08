# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# benchmark_generator.py - Generates carved volumes for cloned-repo algorithm benchmarking

import numpy as np
from pathlib import Path
import random

# tests/data directory
benchmark_dir = Path(__file__).resolve().parent
benchmark_dir.mkdir(exist_ok=True)

def tunnel_excavater(size = 100, n_steps = 20000, branch_prob = 0.02, radius = 1, seed=0):
    """
    Given an empty grid volume of default volume 100^3.

    Produces a volume with randomly carved tunnels within that grid volume.

    Tunnel/excavated widths depend on radius parameter.
    """

    rng = random.Random(seed)

    # fill size^3 volume with 0s (represents solid e.g soil within an excavated ant nest)
    vol = np.zeros((size,size,size), dtype=np.uint8)

    def excavate(position):
        """
        Takes current position and excavates by the radius provided (radius = 1 -> 3x3 excavation)  
        
        Sets thosecells to 1 i.e. excavated  
        """

        # get current coordinates of 'position'
        x,y,z = position
        # define low and high positions for carving given radius
        low = [max(0, x-radius), max(0, y-radius), max(0, z-radius)]
        high = [min(size, x + radius + 1), min(size, y + radius + 1), min(size, z + radius + 1)]

        # ****actual excavation step i.e. set carved volume == 1**** 
        vol[low[0]:high[0], low[1]:high[1], low[2]:high[2]] = 1

    # begin 'excavation' with starting position in centre of volume
    start = (size // 2, size //2, size //2)
    excavate(start)

    # active walker list (like an ant)
    heads = [start]
    # define how the head/ant can move (one unit in all 6 directions in this xyz space)
    moves = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]

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
# 100^3 default size version. ant-nest like optimised
a = tunnel_excavater(seed=10, n_steps=30000, branch_prob=0.0001, radius=1)

# small 15^3 variant (smaller radius for narrower tunnels)
b = tunnel_excavater(size=20, seed=6, n_steps=1000, branch_prob=0.0001, radius=0)

# large 150^3 variant
c = tunnel_excavater(size=125, seed=4, n_steps=50000, branch_prob=0.0001, radius=1)

# 22^3 variant
d = tunnel_excavater(size=45, seed=4, n_steps=12000, branch_prob=0.0001, radius=0)


# saving out the .npy volumes
np.save(benchmark_dir / "nest_bm.npy", a)
np.save(benchmark_dir / "nest_small_bm.npy", b)
np.save(benchmark_dir / "nest_large_bm.npy", c)
np.save(benchmark_dir / "nest_medium_bm.npy", d)


# some infor printed out about % of excavated volume  
print(f"nest_bm.npy: {a.sum()} open voxels of {a.size} ({100*a.sum()/a.size:.2f}%)")
print(f"nest_small_bm.npy: {b.sum()} open voxels of {b.size} ({100*b.sum()/b.size:.2f}%)")
print(f"nest_large_bm.npy: {c.sum()} open voxels of {c.size} ({100*c.sum()/c.size:.2f}%)")
print(f"nest_medium_bm.npy: {d.sum()} open voxels of {d.size} ({100*d.sum()/d.size:.2f}%)")