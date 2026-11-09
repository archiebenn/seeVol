# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# quickstart.py - A minimal python example of seevol

import numpy as np
import seevol

# 0 = empty, 1 = solid
volume = np.zeros((3, 3, 3), dtype=np.uint8)

# adds an obstruction
volume[1, 1, 1] = 1

# calculate pairwise voxel visibility
coords, edges = seevol.visibility_graph(volume)

print(f"{len(coords)} open voxels containing {len(edges)} visible pairs")
