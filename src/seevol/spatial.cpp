/* 
spatial.cpp - spatial graph analyses for voxel-based volumes 
date started: 04-11-26
author: Archie Benn sj19031@bristol.ac.uk
*/  

#include "spatial.hpp"
#include <stdexcept>

std::pair<pybind11::array_t<int>, pybind11::array_t<int>> bfs_distances( pybind11::array_t<uint8_t> volume, int x0, int y0, int z0){
        
    // fast read access to the 3D numpy array
    auto accessor = volume.unchecked<3>();

    // volume size in x,y,z - cached instead of calling accessor(0), etc...
    int x_dim = accessor.shape(0);
    int y_dim = accessor.shape(1);
    int z_dim = accessor.shape(2);

    // guard if input voxels fall outside volume
    if (x0 < 0 || y0 < 0 || z0 < 0 ||
        x0 >= x_dim || y0 >= y_dim || z0 >= z_dim)
        throw std::out_of_range("Start voxel coordinates are outside the volume");

    // flattened 1D array lookup table same size as volume 
    // each entry stores index into open_voxels for that voxel
    // all at -1 initially, and stays at -1 if closed i.e. not in open_voxels
    std::vector<int> index_map(x_dim * y_dim * z_dim, -1);

    // 3d coords (x,y,z) -> single index in index_map
    // required as index_map is 1D not 3D
    auto flat = [&](int x, int y, int z) { return (x * y_dim + y) * z_dim + z; };

    // this will hold the x,y,z coordinates of every open voxel found in the volume
    // voxel's index becomes voxel's 'id' - easier than working with coords
    std::vector<Vec3i> open_voxels;

    // loop over every voxel in the volume - accessor.shape<(0,1,2)> = size of volume in x,y,z axes  
    // only keep voxels which are open (== 1)
    for (int x = 0; x < accessor.shape(0); ++x)
        for (int y =0; y < accessor.shape(1); ++y)
            for (int z = 0; z < accessor.shape(2); ++z)

                // if an open voxel
                if (accessor(x,y,z) != 0) {

                    // set voxel id to next free slot in open_voxels
                    // i.e. index_map id = current size of the open_voxels vector
                    index_map[flat(x,y,z)] = (int)open_voxels.size();

                    // now actually record open voxel (== 1) coordinates into open_voxels  
                    open_voxels.push_back({x, y, z}); 
                }

    // n = total number of free/open voxels found
    const size_t n = open_voxels.size();

    // look up id of starting voxel in index map
    int start_idx = index_map[flat(x0,y0,z0)];

    // if not an open_voxel it will still be -1 as unchanged from above loop
    if (start_idx == -1)
        throw std::runtime_error("Start voxel is not open (1)");
    
    // dist[i] holds BFS distance from start voxel to open_voxels[i]
    // -1 means unreachable or not reached yet 
    std::vector<int> dist(open_voxels.size(), -1);

    // BFS uses a queue of ids (indices into open_voxels)  
    std::queue<int> q;

    // seed the queue with the distance to start voxel
    // distance = 0 as it is distance to self
    dist[start_idx] =0;
    // push into queue
    q.push(start_idx);

    // 6 face neighbour directions: +-x, +-y, +-z for voxel (face-adjacent)
    // these static triples indicate possible offsets
    // TODO: change this algorithm to allow diagonal e.g Dijkstra's  
    // this would then have 26 
    static const int dx[6] = {1,-1,0,0,0,0};
    static const int dy[6] = {0,0,1,-1,0,0};
    static const int dz[6] = {0,0,0,0,1,-1};

    // main BFS loop: keep 'popping' voxels off front of queue until all have been explored
    // see https://www.youtube.com/watch?v=xlVX7dXLS64&t=45s for a great visual explanation to algorithm
    while(!q.empty()) {

        // take next voxel id to process and remove/pop off queue
        int cur = q.front();
        q.pop();

        // access actual coords to compute neighbours
        Vec3i p = open_voxels[cur];

        // check each neighbour in the 6 faces of p 
        for (int d = 0; d < 6; ++d) {
            int nx = p.x + dx[d];
            int ny = p.y + dy[d];
            int nz = p.z + dz[d];

            // skip neighbours of edge voxels on volume i.e. outside volume
            if (nx < 0 || ny < 0 || nz < 0 || nx >= x_dim || ny >= y_dim || nz >= z_dim)
                continue;

            // look up this neighbours if via index_map
            int nidx = index_map[flat(nx,ny,nz)];

            // skip on two conditions:
            // nidx = -1 means neighbour is closed, skip
            // dist[nidx] != -1 means it has already been visited 
            // BFS guaranteed first visit = shortest distance so gets discarded
            if (nidx == -1 || dist[nidx] != -1)
                continue;

            // this is fiurst time reaching this neighbour voxel
            // therefore distance to start voxel is +1 from the one we reached it from
            dist[nidx] = dist[cur] +1;

            // add this neighbour to the queue so we later explore its neighbours too
            q.push(nidx); 
        }
    }

    // queue is now empty so all accessible voxel distances calculated from start
    // pack open voxel coords into an N x 3 numpy array with 1D array of distances to start voxel
    auto coords = pybind11::array_t<int>({(long)n, (long)3});
    auto coords_acc = coords.mutable_unchecked<2>();
    auto distances = pybind11::array_t<int>((pybind11::ssize_t)n);
    auto d = distances.mutable_unchecked<1>();

    // for all open voxel coordinates:
    for (size_t i = 0; i < n; ++i) {
        coords_acc(i, 0) = open_voxels[i].x;
        coords_acc(i, 1) = open_voxels[i].y;
        coords_acc(i, 2) = open_voxels[i].z;
        // attach distance to start voxel
        d(i) = dist[i];
    }

    return {coords, distances};
}