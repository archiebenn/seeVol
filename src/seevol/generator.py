# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# generator.py - Generates example binary NumPy volumes to simulate ant nest excavations/intricate tunnel structures

import numpy as np
import random


def excavate_tunnels(size=100, n_steps=20000, branch_prob=1e-5, radius=1, seed=0):
    """
    Creates a solid grid volume (default volume 100^3 voxels) with excavated tunnels.

    Produces a volume with fully-connected and randomly carved tunnels within that grid volume.
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

    # begin excavation with starting position/head near top in centre
    starting_head = (size // 2, size - 1, size // 2)
    excavate(starting_head)

    # active excavators list - starts with just one
    heads = [starting_head]

    # apply a slight -y bias for increased chance of excavating down (more ant-like)
    # (change these values in each axes to adjust overall excavation shapes)
    moves = (
        [(1, 0, 0)] * 20  # x
        + [(-1, 0, 0)] * 20  # -x
        + [(0, 1, 0)] * 20  # y
        + [(0, -1, 0)] * 22  # -y
        + [(0, 0, 1)] * 20  # z
        + [(0, 0, -1)] * 20  # -z
    )

    for _ in range(n_steps):

        # at every step select one random excavator head + selects new coordinates
        head_idx = rng.randrange(len(heads))
        x, y, z = heads[head_idx]
        dx, dy, dz = rng.choice(moves)
        nx, ny, nz = x + dx, y + dy, z + dz  # new head coordinates

        # only excavates if the new coordinates are within size of volume
        if 0 <= nx < size and 0 <= ny < size and 0 <= nz < size:
            
            # excavate at new coords and update head coordinates
            excavate((nx, ny, nz))
            heads[head_idx] = (nx, ny, nz)

            # occasionally start/add new head at current position
            if rng.random() < branch_prob:
                heads.append((nx, ny, nz))

    return vol
