# Claude exact drop in for my .cpp file, just to test time in Python vs. C++
# NOT authored by me

from seevol.ray_occlusion_cpp import visible_pairs

import time
import numpy as np
from pathlib import Path

def get_voxel_value(volume, x, y, z):
    return np.uint8(volume[x, y, z])

def is_visible_py(volume, x0, y0, z0, x1, y1, z1):
    if volume[x0, y0, z0] == 0 or volume[x1, y1, z1] == 0:
        return False

    pos = [x0, y0, z0]
    end = (x1, y1, z1)
    d = (x1 - x0, y1 - y0, z1 - z0)

    step = [1 if v >= 0 else -1 for v in d]
    inf = float("inf")                      # C++ 1.0/0 -> inf
    delta = [abs(1.0 / v) if v != 0 else inf for v in d]
    tmax = [0.5 * v for v in delta]

    while tuple(pos) != end:
        # identical branch order to the C++ (matters for ties)
        if tmax[0] < tmax[1]:
            ax = 0 if tmax[0] < tmax[2] else 2
        else:
            ax = 1 if tmax[1] < tmax[2] else 2
        pos[ax] += step[ax]
        tmax[ax] += delta[ax]
        if volume[pos[0], pos[1], pos[2]] == 0:
            return False
    return True

def visible_pairs_py(volume):
    volume = np.asarray(volume, dtype=np.uint8)
    coords = np.argwhere(volume != 0).astype(np.int32)   # same x,y,z loop order
    pts = coords.tolist()
    n = len(pts)
    edges = []
    for i in range(n):
        a = pts[i]
        for j in range(i + 1, n):
            b = pts[j]
            if is_visible_py(volume, *a, *b):
                edges.append((i, j))
    edge_arr = np.array(edges, dtype=np.int32).reshape(-1, 2)
    return coords, edge_arr



### TESTING ###
if __name__ == "__main__":
    benchmark_dir = Path(__file__).resolve().parent
    vol = np.load(benchmark_dir / "nest_medium_bm.npy")

    t0 = time.perf_counter()
    c_cpp, e_cpp = visible_pairs(vol)
    t_cpp = time.perf_counter() - t0

    t0 = time.perf_counter()
    c_py, e_py = visible_pairs_py(vol)
    t_py = time.perf_counter() - t0

    assert np.array_equal(c_py, c_cpp) and np.array_equal(e_py, e_cpp)
    print(f"open voxels: {len(c_cpp)}  edges: {len(e_cpp)}")
    print(f"C++:    {t_cpp:.5f}s")
    print(f"Python: {t_py:.5f}s  ({t_py / t_cpp:.0f}x slower)")