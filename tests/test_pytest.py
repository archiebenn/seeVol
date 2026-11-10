# Copyright (c) 2026 Archie Benn
#
# This software is licensed under the MIT License.
# See the LICENSE file in the project root for the full license text.
#
# test_pytest.py - Tests seeVol functions with pytest

import numpy as np
import pytest
from itertools import combinations, product
from fractions import Fraction
import seevol


# test binary swap works for 0<->1 NumPy conversion
def chech_binary_swap():

    # create sample volume
    volume = np.zeros((3, 3, 3), dtype=np.uint8)

    assert volume[0, 0, 0] == 0
    volume = seevol.binary_swap(volume)  # invert
    assert volume[0, 0, 0] == 1
    volume = seevol.binary_swap(volume)  # re-invert
    assert volume[0, 0, 0] == 0


# check 5^3 fully open/0 volume
def test_open_volume_visible():

    vol = np.zeros((5, 5, 5), dtype=np.uint8)
    assert seevol.is_visible(vol, 0, 0, 0, 4, 4, 4)


# check visibility of 2 voxels in 5^3 with a solid/1 voxel
def test_wall_blocks_diagonal():

    vol = np.zeros((5, 5, 5), dtype=np.uint8)
    vol[2, 2, 2] = 1
    assert not seevol.is_visible(vol, 0, 0, 0, 4, 4, 4)
    assert seevol.is_visible(vol, 0, 0, 0, 0, 0, 4)


# same as above but testing main pair count function for reduction of visible pairs
def test_wall_reduces_visible_pairs():

    vol = np.zeros((5, 5, 5), dtype=np.uint8)
    vol2 = vol.copy()
    vol2[2, 2, 2] = 1

    # number of visible pairs should drop in volume with wall
    _, edges = seevol.visibility_graph(vol)
    coords2, edges2 = seevol.visibility_graph(vol2)
    assert edges2.shape[0] < edges.shape[0]
    assert not np.any(np.all(coords2 == [2, 2, 2], axis=1))


def brute_force_bounds(vol, a, b):
    """
    Brute force: returns strict (strict, lenient) visibility between open voxels a <-> b

    Strict = visibility is only true if ray segment touches no solid voxel at all

    Lenient = visibility can also be true if ray segment grazes corner of solid voxel
    (e.g. in exact diagonal where open voxel is adjacent to a closed voxel on the corner the ray goes through)
    """

    # work in doubled coordinates so everything stays an integer: centre = 2i+1, voxel = [2i, 2i+2]
    # ray start = centre of voxel a
    A = [2 * i + 1 for i in a]
    # ray direction vector (centre of b - centre of a)
    d = [2 * (j - i) for i, j in zip(a, b)]
    # highest and lowest voxel indices ray can touch for each axis
    lo_v = [min(i, j) for i, j in zip(a, b)]
    hi_v = [max(i, j) for i, j in zip(a, b)]

    # touches: segment touches a solid voxel at all (including corners/edges)
    touches = False
    # crosses: segment passes through a solid voxel's interior
    crosses = False

    # loop over every voxel in the bounding box of the two endpoints
    for v in product(*[range(l, h + 1) for l, h in zip(lo_v, hi_v)]):
        if vol[v] == 0:
            continue
        t0, t1 = Fraction(0), Fraction(1)
        inside_open = True
        for k in range(3):
            lo, hi = 2 * v[k], 2 * v[k] + 2
            if d[k] == 0:
                if not lo <= A[k] <= hi:
                    t0, t1 = Fraction(1), Fraction(0)
                if not lo < A[k] < hi:
                    inside_open = False
            else:
                ta, tb = Fraction(lo - A[k], d[k]), Fraction(hi - A[k], d[k])
                t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
        if t0 <= t1:
            touches = True
            if t0 < t1 and inside_open:
                crosses = True
    return not touches, not crosses


# pytest: assert that brute force and my C++ function arrive at the same results for visibility algorithm
# run over 15 seeds for random
@pytest.mark.parametrize("seed", range(15))
def test_matches_brute_force(seed):
    """C++ result must lie between the strict and lenient brute-force answers."""

    rng = np.random.default_rng(seed)

    # 6^3 volume with 30% chance per voxel being set to solid (1)
    vol = (rng.random((6, 6, 6)) <= 0.3).astype(np.uint8)

    # np.argwhere(vol == 0) returns coordinates of open voxels only
    open_vox = [tuple(int(v) for v in p) for p in np.argwhere(vol == 0)]

    # every unique voxel pair, only once
    for a, b in combinations(open_vox, 2):
        # lowest and higehest acceptable answers
        strict, lenient = brute_force_bounds(vol, a, b)
        cpp = seevol.is_visible(vol, *a, *b)
        # assert that C++ result falls between these strict/lenient bounds
        assert strict <= cpp <= lenient, (
            f"seed={seed} a={a} b={b} C++={cpp} strict={strict} lenient={lenient}"
        )


# ensure that visibility_scores (memory improvements for score visualisation only) matches visible_pairs main graph
def test_scores_and_edges():

    rng = np.random.default_rng(0)
    # vol about 75% open (0) randomly allocated
    vol = (rng.random((20, 20, 20)) <= 0.25).astype(np.uint8)

    coords, edges = seevol.visibility_graph(vol)
    coords2, scores = seevol.visibility_scores(vol)
    assert (coords == coords2).all()
    assert (np.bincount(edges.ravel(), minlength=len(coords)) == scores).all()
