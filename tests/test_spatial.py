import numpy as np
import pytest

import seevol


def test_bfs_distances_on_open_voxels():
    volume = np.ones((3, 1, 1), dtype=np.uint8)
    volume[:, 0, 0] = 0

    coords, distances = seevol.bfs_distances(volume, 0, 0, 0)

    np.testing.assert_array_equal(coords, [[0, 0, 0], [1, 0, 0], [2, 0, 0]])
    np.testing.assert_array_equal(distances, [0, 1, 2])

def test_tunnel_excavator_uses_zero_for_excavated_voxels():
    volume = seevol.tunnel_excavator(size=3, n_steps=0, radius=0)

    expected = np.ones((3, 3, 3), dtype=np.uint8)
    expected[1, 2, 1] = 0
    np.testing.assert_array_equal(volume, expected)


def test_bfs_distances_rejects_out_of_bounds_start():
    volume = np.zeros((2, 2, 2), dtype=np.uint8)

    with pytest.raises(IndexError, match="outside the volume"):
        seevol.bfs_distances(volume, 2, 0, 0)


def test_bfs_distances_rejects_closed_start():
    volume = np.ones((2, 2, 2), dtype=np.uint8)

    with pytest.raises(RuntimeError, match="not open"):
        seevol.bfs_distances(volume, 0, 0, 0)
