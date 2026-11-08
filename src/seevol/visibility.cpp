// Copyright (c) 2026 Archie Benn
//
// This software is licensed under the MIT License.
// See the LICENSE file in the project root for the full license text.
//
// visibility.cpp - Ray traversal for visibility analyses of binary 3D volumes
//
// Core line-of-sight approach is based on the algorithm from "Amanatides, J. & Woo, A. A Fast Voxel Traversal Algorithm for Ray Tracing."  
// Guide for algorithm and implementation: https://m4xc.dev/articles/amanatides-and-woo/  

#include "visibility.hpp"
#include <atomic>
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <string>

uint8_t get_voxel_value(pybind11::array_t<uint8_t> volume, int x, int y, int z){

    // .unchecked<3>() gives access to underlying array in Python so doesn't need to load it  
    // auto just automatically detects accessor type, and accessor is just an object pointing to the nummpy array's memory
    auto accessor = volume.unchecked<3>();

    // index into array position from coordinates and return byte value (0 or 1)  
    return accessor(x,y,z);
}


bool is_visible(const Vol& volume, int x0, int y0, int z0, int x1, int y1, int z1){

    // only go forward if both start and end voxels are empty (0)
    if (volume(x0,y0,z0) != 0 || volume(x1,y1,z1) != 0) return false;

    // current position (first voxel initially) and constant end voxel indices/coords
    Vec3i pos = {x0, y0, z0};
    const Vec3i end = {x1, y1, z1};

    // distances in each axes from start to finish
    const int dx = (x1 - x0);
    const int dy = (y1 - y0);
    const int dz = (z1 - z0);

    // compute step direction in each axes based on deltas 
    // step array - 3 ints (each is -1, 0, +1 and represents constant ray direction in  x,y,z axes)  
    Vec3i step;
    if (dx >= 0) { step.x = 1; } else { step.x = -1; } // ray direction in x
    if (dy >= 0) { step.y = 1; } else { step.y = -1; } // ray direction in y
    if (dz >= 0) { step.z = 1; } else { step.z = -1; } // ray direction in z

    // delta array - how far in each axis the ray moves per voxel step (in ray paremeter t in amanatides-woo)
    Vec3d delta;
    delta.x = std::abs(1.0 / dx);
    delta.y = std::abs(1.0 / dy);
    delta.z = std::abs(1.0 / dz);

    // initial tmax array values - half the delta as starting in centre of voxel 
    Vec3d tmax;
    tmax.x = 0.5 * delta.x;
    tmax.y = 0.5 * delta.y;
    tmax.z = 0.5 * delta.z;

    // and now to implement the Amanatides-Woo algorithtm:
    while (pos.x != end.x || pos.y != end.y || pos.z != end.z){

        // step on the axis where tmax is the smallest (from https://m4xc.dev/articles/amanatides-and-woo/)  
        if (tmax.x < tmax.y) {
            if (tmax.x < tmax.z) {
                pos.x += step.x;
                tmax.x += delta.x;
            } else {
                pos.z += step.z;
                tmax.z += delta.z;
            }
        } else {
            if (tmax.y < tmax.z) {
                pos.y += step.y;
                tmax.y += delta.y;
            } else {
                pos.z += step.z;
                tmax.z += delta.z;
            }
        }

        // if the voxel the ray is currently ending at is non-zero/1, it has hit a solid structure
        if (volume(pos.x,pos.y,pos.z) != 0) 
            return false; // early exit
    }

    // ray has been traced from start voxel to finish voxel and line of sight is visible between pair  
    return true;

}


bool is_visible_py(pybind11::array_t<uint8_t> volume, int x0, int y0, int z0, int x1, int y1, int z1){
    return is_visible(volume.unchecked<3>(), x0, y0, z0, x1, y1, z1);
}


std::pair<pybind11::array_t<int>, pybind11::array_t<int>> visibility_graph(pybind11::array_t<uint8_t> volume, bool verbose){

    // .unchecked<3>() gives fast volume(x,y,z) access to the numpy array
    // update to is_visible (29-10-26) means that this is the only time accessor is built now
    // and then passed by reference (const Vol&) to is_visible
    auto accessor = volume.unchecked<3>();

    // volume size in x,y,z - cached instead of calling accessor(0), etc...
    int x_dim = accessor.shape(0);
    int y_dim = accessor.shape(1);
    int z_dim = accessor.shape(2);

    // this will hold the x,y,z coordinates of every empty voxel found in the volume
    // voxel's index becomes voxel's 'id' - easier than working with coords
    std::vector<Vec3i> open_voxels;

    // loop over every voxel in the volume - accessor.shape<(0,1,2)> = size of volume in x,y,z axes  
    // only keep voxels which are empty (== 0)
    for (int x = 0; x < x_dim; ++x)
        for (int y =0; y < y_dim; ++y)
            for (int z = 0; z < z_dim; ++z)
                if (accessor(x,y,z) == 0)
                    // record empty voxel coordinates into open_voxels
                    open_voxels.push_back({x, y, z}); 

    // n = total number of free/open voxels found
    const size_t n = open_voxels.size();

    // protect the program by putting a max limit on open voxel count before computing ray traversals  
    const size_t mo = 1000000;

    if (n > mo){
        throw std::runtime_error(
        "Too many open voxels (n = " + std::to_string(n) +
        ") for O(n^2) visibility computation. Limit is " +
        std::to_string(mo) + "."
    );
    }

    // edges is list of an open voxel<->voxel pair and stored into open_voxels when visibility between pairs is true
    // so each element is a pair of ints (i and j indices in open_voxels) and only when i<->j is visible
    std::vector<std::pair<int,int>> edges;

    // ****HOT LOOP START****
    // outer loop walks every voxel i=0 to i=n-1 in open_voxels
    // this is the main loop which walks through every voxel pair (i, j) and tests occlusion using is_visible
    {

        if (verbose) std::cout << "RUNNING C++ VOXEL RAY-CASTING...\n";

        // atomic long long counter (for terminal completion) - atomic means no two threads can increment at same time
        std::atomic<long long> completed{0};
        pybind11::gil_scoped_release release; // (for multithreading)

        // start a team of threads and each runs this block
        #pragma omp parallel
        {
            // per thread results: avoids a data race from many threads doing push_back into the shared 'edges' object  
            std::vector<std::pair<int,int>> local;

            // split the outer loop across threads. dynamic, 16 = threads grab chunks of 16 rows as they finish
            // which balances the load since early i rows do more work (j = i+1 shrinks as i grows)
            // nowait = don't make threads wait for each other at the end of the loop
            #pragma omp for schedule(dynamic, 16) nowait
            for (long long i = 0; i < (long long)n; ++i)
            {

                // point at voxel i's coordinates stored in open_voxels and store as a
                const Vec3i& a = open_voxels[i];

                // inner loop: symmetry optimisation -> never check the same pair from the opposite direction
                // hence the 'j = i +1' - if i = 0, j runs 1,2,3... and if i = 1 j runs 2,3,4...
                // this stops testing A<->B and then also B<->A as result will be identical
                for (size_t j = (size_t)i + 1; j < n; ++j)
                {
                    // point at voxel j's coordinates stored in open_voxels and store as b
                    const Vec3i& b = open_voxels[j];

                    // so now have 2 voxels (i and j) with coords stored in a and b
                    // so can test visibility between them both with is_visible
                    if (is_visible(accessor, a.x, a.y, a.z, b.x, b.y, b.z))
                    {
                        // if visible, record this pair/edge in this thread's local list
                        local.emplace_back((int)i, (int)j);
                    }
                }

                // a little completion bar for this hot loop to the terminal 
                long long done = ++completed;
                // print every 2500th voxel pair completed
                if (verbose && done % 2500 == 0) {
                    double frac = (double)done / (double)n;
                    int filled = (int)(frac * 40);
                    // \r overwrites previous output and then std::flushg sends straight to terminal  
                    if (verbose) std::cout << "\r[" << std::string(filled, '#') << std::string(40 - filled, '-')
                    << "] " << (int)(frac * 100) << "%" << std::flush;
                }
            }

            // merge this thread's results into the shared edges, one thread at a time
            #pragma omp critical
            edges.insert(edges.end(), local.begin(), local.end());
        }

    }  
    // ****HOT LOOP END****

    if (verbose) std::cout << "\r[" << std::string(40, '#') << "] 100%\n";
    
    // threads finish in nondeterministic order, so sort to get the same output every run
    std::sort(edges.begin(), edges.end());

    // pack open voxel coords into an N x 3 numpy array
    auto coords = pybind11::array_t<int>({(long)n, (long)3});
    auto coords_acc = coords.mutable_unchecked<2>();
    // for all open voxels
    for (size_t i = 0; i < n; ++i) {
        coords_acc(i, 0) = open_voxels[i].x;
        coords_acc(i, 1) = open_voxels[i].y;
        coords_acc(i, 2) = open_voxels[i].z;
    }

    // pack visible edges into an M x 2 numpy array
    const size_t m = edges.size();
    auto edge_arr = pybind11::array_t<int>({(long)m, (long)2});
    auto edge_acc = edge_arr.mutable_unchecked<2>();
    // for all elements in edges list
    for (size_t k = 0; k < m; ++k) {
        edge_acc(k, 0) = edges[k].first;
        edge_acc(k, 1) = edges[k].second;
    }

    return {coords, edge_arr};
}


std::pair<pybind11::array_t<int>, pybind11::array_t<int>> visibility_scores(pybind11::array_t<uint8_t> volume, bool verbose){

    // .unchecked<3>() gives fast volume(x,y,z) access to the numpy array
    // update to is_visible (29-10-26) means that this is the only time accessor is built now
    // and then passed by reference (const Vol&) to is_visible
    auto accessor = volume.unchecked<3>();

    // this will hold the x,y,z coordinates of every empty voxel found in the volume
    std::vector<Vec3i> open_voxels;

    // loop over every voxel in the volume - accessor.shape<(0,1,2)> = size of volume in x,y,z axes  
    // only keep voxels which are empty (== 0)
    for (int x = 0; x < accessor.shape(0); ++x)
        for (int y =0; y < accessor.shape(1); ++y)
            for (int z = 0; z < accessor.shape(2); ++z)
                if (accessor(x,y,z) == 0)
                    // record empty voxel coordinates into open_voxels
                    open_voxels.push_back({x, y, z}); 

    // n = total number of free/open voxels found
    const size_t n = open_voxels.size();

    // visibility scores - n ints starting at 0
    std::vector<int> counts(n, 0);  

    // ****HOT LOOP START****
    // outer loop walks every voxel i=0 to i=n-1 in open_voxels
    // this is the main loop which walks through every voxel pair (i, j) and tests occlusion using is_visible
    {

        if (verbose) std::cout << "RUNNING C++ VOXEL RAY-CASTING...\n";

        // atomic long long counter (for terminal completion) - atomic means no two threads can increment at same time
        std::atomic<long long> completed{0};

        // (for multithreading)
        pybind11::gil_scoped_release release;

        // start a team of threads and each runs this block
        #pragma omp parallel
        {
            // this thread's count 
            std::vector<int> local(n, 0);

            // split the outer loop across threads. dynamic, 16 = threads grab chunks of 16 rows as they finish
            #pragma omp for schedule(dynamic, 16) nowait
            for (long long i = 0; i < (long long)n; ++i)
            {

                // point at voxel i's coordinates stored in open_voxels and store as a
                const Vec3i& a = open_voxels[i];

                // inner loop: symmetry optimisation -> never check the same pair from the opposite direction
                for (size_t j = (size_t)i + 1; j < n; ++j)
                {
                    // point at voxel j's coordinates stored in open_voxels and store as b
                    const Vec3i& b = open_voxels[j];

                    // test visibility between voxels (i and j) with coords stored in a and b
                    if (is_visible(accessor, a.x, a.y, a.z, b.x, b.y, b.z))

                    // if visible to each other, +1 to each voxel's visibility counter
                    {
                        ++local[i];
                        ++local[j];
                    }
                }

                // a little completion bar for this hot loop to the terminal 
                long long done = ++completed;
                // print every 2500th voxel pair completed
                if (verbose && done % 2500 == 0) {
                    double frac = (double)done / (double)n;
                    // how many #s to show
                    int filled = (int)(frac * 40);
                    // \r overwrites previous output and then std::flushg sends straight to terminal  
                    if (verbose) std::cout << "\r[" << std::string(filled, '#') << std::string(40 - filled, '-')
                    << "] " << (int)(frac * 100) << "%" << std::flush;
                }
            }

            // merge this thread's results into the shared edges, one thread at a time to get all open voxel results
            #pragma omp critical
            for (size_t k = 0; k < n; ++k) counts[k] += local[k];
        }

    }  
    // ****HOT LOOP END****

    // 100% completion to terminal
    if (verbose) std::cout << "\r[" << std::string(40, '#') << "] 100%\n";

    // pack open voxel coords into an N x 3 numpy array with 1D array of scores
    auto coords = pybind11::array_t<int>({(long)n, (long)3});
    auto coords_acc = coords.mutable_unchecked<2>();
    auto scores = pybind11::array_t<int>((pybind11::ssize_t)n);
    auto s = scores.mutable_unchecked<1>();
    
    // for all open voxel coordinates:
    for (size_t i = 0; i < n; ++i) {
        coords_acc(i, 0) = open_voxels[i].x;
        coords_acc(i, 1) = open_voxels[i].y;
        coords_acc(i, 2) = open_voxels[i].z;
        // attach score
        s(i) = counts[i];
    }

    return {coords, scores};
}

