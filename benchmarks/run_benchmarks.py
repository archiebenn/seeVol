# benchmarks.py - benchmarking C++ timings on algorithm over time with development  
# author: Archie Benn sj19031@bristol.ac.uk 
# date: 28-10-26  

import csv, datetime, subprocess
import numpy as np
import time
import platform, os
from pathlib import Path
from seevol.ray_occlusion_cpp import visible_pairs

benchmark_dir = Path(__file__).resolve().parent
csv_path = benchmark_dir / "benchmarks.csv"

print("What computer is running this benchmark?")
computer_name = input()

# load benchmark artifical nest volumes
small_20_nest = np.load(benchmark_dir / "nest_small_bm.npy")
small_medium_45_nest = np.load(benchmark_dir / "nest_medium_bm.npy")
medium_100_nest = np.load(benchmark_dir / "nest_bm.npy")
large_150_nest = np.load(benchmark_dir / "nest_large_bm.npy")

# get current commit for tracking over time
commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True, text=True).stdout.strip()

# benchmark timer
def benchmark(name, vol, repeats=3, computer = computer_name):

    print("***BENCHMARK RUNNING***")

    times = []

    for _ in range(repeats):
        t0 = time.perf_counter()
        # run C++ hot loop
        coords, edges = visible_pairs(vol)
        times.append(time.perf_counter() - t0)
    t_cpp = min(times)

    n = len(coords)
    n_rays = n * (n - 1) // 2
    row = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "computer": computer,
        "git_commit": commit,
        "volume_name": name,
        "volume_shape": "x".join(map(str, vol.shape)),
        "open_voxels": n,
        "n_rays": n_rays,
        "visible_pairs": len(edges),
        "t_cpp_s": round(t_cpp, 6),
        "us_per_ray": round(t_cpp / n_rays * 1e6, 5),
    }
    print(row)

    new = not csv_path.exists()
    with csv_path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if new:
            w.writeheader()
        w.writerow(row)


# run benchmarks
benchmark("small_20", small_20_nest, repeats=3)
benchmark("small_medium_45", small_medium_45_nest, repeats=1)
benchmark("medium_100", medium_100_nest, repeats=3)
#benchmark("large_150", large_150_nest, repeats=1)

print("***BENCHMARK COMPLETE***")