/* woo_test.cpp - small scale testing of ray-tracing  
based on an algorithm from "Amanatides, J. & Woo, A. A Fast Voxel Traversal Algorithm for Ray Tracing."  
guide for algorithm and implementation: https://m4xc.dev/articles/amanatides-and-woo/  
date started: 26-10-2026  
author: Archie Benn sj19031@bristol.ac.uk
*/  

#include <omp.h>
#include <atomic>
#include <iostream>
#include <vector>
#include <cstdint>
#include <utility>
#include <cmath>
#include <algorithm>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>


/**
 * Return voxel value (0 or 1) from numpy array (3D volume)
 * For testing C++ <-> Python indexing  
 *
 * @param volume numpy np.uint8 data type
 * @param x voxel index along the x axis
 * @param y voxel index along the y axis
 * @param z voxel index along the z axis
 * @return byte value of voxel from coordinates  
 */
uint8_t get_voxel_value(pybind11::array_t<uint8_t> volume, int x, int y, int z){

    // .unchecked<3>() gives access to underlying array in Python so doesn't need to load it  
    // auto just automatically detects accessor type, and accessor is just an object pointing to the nummpy array's memory
    auto accessor = volume.unchecked<3>();

    // index into array position from coordinates and return byte value (0 or 1)  
    return accessor(x,y,z);
}

// 2 structs: 3 integer and 3 double
struct Vec3i {int x, y, z;};
struct Vec3d {double x, y, z;};

// type alias for the volume. unchecked_reference gives access to underlying array in Python so doesn't need to load it 
// i.e. gives raw view to the numpy array   
// making this alias and passing by reference in is_visible stops accessor being rebuilt on every is_visible loop
using Vol = pybind11::detail::unchecked_reference<uint8_t, 3>;

/**
 * Return if a **single** pair of voxels is visible to each other in a straight line without being occluded by a solid/0 voxel  
 * Using "Amanatides, J. & Woo, A. A Fast Voxel Traversal Algorithm for Ray Tracing." algorithm  
 *
 * @param volume read-only view of the 3D uint8 numpy volume
 * @param x0 start voxel index along the x axis
 * @param y0 start voxel index along the y axis
 * @param z0 start voxel index along the z axis
 * @param x1 end voxel index along the x axis
 * @param y1 end voxel index along the y axis
 * @param z1 end voxel index along the z axis
 * @return BOOL for whether visible in line or sight (true) or not (false)    
 */
bool is_visible(const Vol& volume, int x0, int y0, int z0, int x1, int y1, int z1){

    // only go forward if both start and end voxels == 1 i.e. open voxels  
    if (volume(x0,y0,z0) == 0 || volume(x1,y1,z1) == 0) return false;

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

    // and now to implement the actual Amanatides-Woo algorithtm:
    while (pos.x != end.x || pos.y != end.y || pos.z != end.z){

        // step on the axis where tmax is the smallest (from website guide)  
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

        // with the current pos ('or current ray end') location, access the byte value in the volume/.npy array:
        // if the voxel the ray is currently ending at == 0, the ray has hit a solid structure and return false
        // this is **early exit**  
        if (volume(pos.x,pos.y,pos.z) == 0) return false;
    }

    // ray has been traced from start voxel to finish voxel, so return true (line of sight is visible between pair)  
    return true;

}

// for python import after changing the parameters for main is_visible
bool is_visible_py(pybind11::array_t<uint8_t> volume, int x0, int y0, int z0, int x1, int y1, int z1){
    return is_visible(volume.unchecked<3>(), x0, y0, z0, x1, y1, z1);
}

/**
 * Compute all visible pairs of free voxels in the volume.
 * One call from Python; returns the free voxel coordinates plus the list of visible (i, j) index pairs into that list.
 *
 * @param volume numpy np.uint8 data type
 * @return pair of: (N x 3 int array of free voxel coordinates, M x 2 int array of visible index pairs)
 */
std::pair<pybind11::array_t<int>, pybind11::array_t<int>> visible_pairs(pybind11::array_t<uint8_t> volume){

    // .unchecked<3>() gives fast volume(x,y,z) access to the numpy array
    // update to is_visible (29-10-26) means that this is the only time accessor is built now
    // and then passed by reference (const Vol&) to is_visible
    auto accessor = volume.unchecked<3>();

    // this will hold the x,y,z coordinates of every open voxel found in the volume
    std::vector<Vec3i> open_voxels;

    // loop over every voxel in the volume - accessor.shape<(0,1,2)> = size of volume in x,y,z axes  
    // only keep voxels which are open (== 1)
    for (int x = 0; x < accessor.shape(0); ++x)
        for (int y =0; y < accessor.shape(1); ++y)
            for (int z = 0; z < accessor.shape(2); ++z)
                if (accessor(x,y,z) != 0)
                    // record voxel (== 1) coordinates into open_voxels  
                    open_voxels.push_back({x, y, z}); 

    // n = total number of free/open voxels found
    const size_t n = open_voxels.size();

    // edges is list of an open voxel<->voxel pair and stored into open_voxels when visibility between pairs is true
    // so each element is a pair of ints (i and j indices in open_voxels) and only when i<->j is visible
    std::vector<std::pair<int,int>> edges;

    // ****HOT LOOP START****
    // outer loop walks every voxel i=0 to i=n-1 in open_voxels
    // this is the main loop which walks through every voxel pair (i, j) and tests occlusion using is_visible
    {

        std::cout << "RUNNING C++ VOXEL RAY-CASTING...\n";

        // atomic long long counter (for terminal completion) - atomic means no two threads can increment at same time
        std::atomic<long long> completed{0};

        // (for multithreading)
        pybind11::gil_scoped_release release;

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
                        // if visible, record this pair in this thread's local list
                        local.emplace_back((int)i, (int)j);
                    }
                }

                // a little completion bar for this hot loop to the terminal 
                long long done = ++completed;
                // print every 2500th voxel pair completed
                if (done % 2500 == 0) {
                    double frac = (double)done / (double)n;
                    // how many #s to show
                    int filled = (int)(frac * 40);
                    // \r overwrites previous output and then std::flushg sends straight to terminal  
                    std::cout << "\r[" << std::string(filled, '#') << std::string(40 - filled, '-')
                    << "] " << (int)(frac * 100) << "%" << std::flush;
                }
            }

            // merge this thread's results into the shared edges, one thread at a time
            #pragma omp critical
            edges.insert(edges.end(), local.begin(), local.end());
        }

    }  
    // ****HOT LOOP END****

    // 100% completion to terminal
    std::cout << "\r[" << std::string(40, '#') << "] 100%\n";

    // threads finish in nondeterministic order, so sort to get the same output every run
    std::sort(edges.begin(), edges.end());

    // pack open voxel coords into an N x 3 numpy array
    auto coords = pybind11::array_t<int>({(long)n, (long)3});
    auto coords_acc = coords.mutable_unchecked<2>();
    // for all open voxel coordinates:
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

// pybind module - (occlusion_cpp must match name in CMakeLists.txt)  
PYBIND11_MODULE(ray_occlusion_cpp, m) {
    m.def("get_voxel_value", &get_voxel_value, "Return voxel value (0 or 1) from numpy array (3D volume)");
    m.def("is_visible", &is_visible_py, "Return whether a single voxel pair has line of sight");
    m.def("visible_pairs", &visible_pairs, "Computes all visible voxel pairs in a volume and returns Nx3 int array of open voxel coordinates as well a linked Mx2 array of visible index pairs");
}

