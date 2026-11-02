# test_oracle.py - tests C++ amanatides-woo algorithm implementation and the main visible_pairs
# date: 29-10-2026  
# author: Archie Benn sj19031@bristol.ac.uk (+ Claude for pytest guidance)  

import numpy as np
import pytest
from itertools import combinations, product
from fractions import Fraction
from seevol.voxel_occlusion import is_visible, visible_pairs

# check 5^3 fully open/1 volume 
def test_open_volume_visible():
    vol = np.ones((5, 5, 5), dtype=np.uint8)
    assert is_visible(vol, 0, 0, 0, 4, 4, 4)

# check 5^3 with a closed/0 voxel 
def test_wall_blocks_diagonal():
    vol = np.ones((5, 5, 5), dtype=np.uint8)
    vol[2, 2, 2] = 0
    assert not is_visible(vol, 0, 0, 0, 4, 4, 4)
    assert is_visible(vol, 0, 0, 0, 0, 0, 4)

# same as above but testing main pair count function for reduction of visible pairs
def test_wall_reduces_visible_pairs():
    vol = np.ones((5, 5, 5), dtype=np.uint8)
    vol2 = vol.copy(); vol2[2, 2, 2] = 0
    # number of visible pairs should drop in volume with wall 
    _, edges = visible_pairs(vol)
    _, edges2 = visible_pairs(vol2)
    assert edges2.shape[0] < edges.shape[0]

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
        if vol[v]:
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

    # 6^3 volume with 70% chance per voxel being set to open (1)  
    vol = (rng.random((6, 6, 6)) > 0.3).astype(np.uint8)

    # np.argwhere(vol) returns coordinates of non empty (i.e. open) voxels only  
    # so open_vox is a list of tuples of coords for open voxels in volume  
    open_vox = [tuple(int(v) for v in p) for p in np.argwhere(vol)]

    # every unique voxel pair, only once  
    for a, b in combinations(open_vox, 2):

        # lowest and higehest acceptable answers  
        strict, lenient = brute_force_bounds(vol, a, b)
        cpp = is_visible(vol, *a, *b)
        # assert that C++ result falls between these strict/lenient bounds  
        assert strict <= cpp <= lenient, (
            f"seed={seed} a={a} b={b} C++={cpp} strict={strict} lenient={lenient}"
        )