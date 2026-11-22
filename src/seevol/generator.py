# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# generator.py - Generates example binary NumPy volumes to simulate ant nest excavations/intricate tunnel structures

import numpy as np
import random


def excavate_tunnels(size=200, n_steps=15000, branch_prob=1e-3, radius=1, seed=0):
    """
    - Creates a volume (default volume 150^3 voxels) with excavated tunnels.
    - Volume with fully-connected and randomly carved tunnels within that grid volume.
    - 2 main excavation phases involved: Early (x/z biased) and Established (-y biased) excavation from head units ("ants")  
    """

    rng = random.Random(seed)
    vol = np.ones((size, size, size), dtype=np.uint8)

    def excavate(position):
        """
        Takes current position and excavates by the radius provided (radius = 1 -> 3x3 excavation).

        Sets 'excavated' voxel cells to 0.
        """

        # get 3D coordinates of 'position' and define high/low based on radius
        x, y, z = position
        low = [max(0, x - radius), max(0, y - radius), max(0, z - radius)]
        high = [
            min(size, x + radius + 1),
            min(size, y + radius + 1),
            min(size, z + radius + 1),
        ]

        # excavation step i.e. set carved voxel(s) == 0
        vol[low[0] : high[0], low[1] : high[1], low[2] : high[2]] = 0

    # begin excavation with starting position/head near top in centre (+ 1000 as step counter for first head only)
    starting_head = [size // 2, size - 1, size // 2, size*7]
    excavate(starting_head[0:3]) # x,y,z passed to excavator function

    # active excavators list (of lists) - starts with just one
    # each individual head/excavator will be [x, y, z, steps]
    heads = [starting_head]

    # first steps for each new head have an x and z bias (mimics ant chambers)
    # (change these values in each axes to adjust overall excavation shapes)
    moves_early = (
        [(1, 0, 0)] * 50  # x
        + [(-1, 0, 0)] * 50  # -x
        + [(0, 1, 0)] * 1  # y
        + [(0, -1, 0)] * 1  # -y
        + [(0, 0, 1)] * 50  # z
        + [(0, 0, -1)] * 50  # -z
    )

    # for established and original head, apply a slight -y bias for increased chance of excavating down (more ant-like)
    # (change these values in each axes to adjust overall excavation shapes)
    moves_established = (
        [(1, 0, 0)] * 5  # x
        + [(-1, 0, 0)] * 5  # -x
        + [(0, 1, 0)] * 10  # y
        + [(0, -1, 0)] * 12  # -y
        + [(0, 0, 1)] * 5  # z
        + [(0, 0, -1)] * 5  # -z
    )

    for _ in range(n_steps):

        # at every step select one random excavator head + selects new coordinates
        head_idx = rng.randrange(len(heads))
        # sets current location for excavation as first 3 values in sleected head
        x, y, z = heads[head_idx][0:3]
        # gets current step count of head
        head_steps = heads[head_idx][-1]

        # condition decides which move list to use (x- or y- bias) based on size of volume
        if head_steps <= size*7:
            dx, dy, dz = rng.choice(moves_early)
        else:
            dx, dy, dz = rng.choice(moves_established)

        # new head coordinates
        nx, ny, nz = x + dx, y + dy, z + dz  

        # only excavates if the new coordinates are within size of volume
        if 0 <= nx < size and 0 <= ny < size and 0 <= nz < size:
            # excavate at new coords and update head coordinates
            excavate((nx, ny, nz))
            heads[head_idx][0:3] = (nx, ny, nz)

            # add to step count
            new_steps = head_steps +1
            heads[head_idx][-1] = new_steps

            # occasionally start/add new head at current position
            if rng.random() < branch_prob:

                # new head starts at these new coords and has step counter set to 0
                heads.append([nx, ny, nz, 0]) 

    print(f"Volume generated with {len(heads)} excavating heads over {n_steps} steps.")
    return vol


