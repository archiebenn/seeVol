// Copyright (c) 2026 Archie Benn
//
// This software is licensed under the MIT License.
// See the LICENSE file in the project root for the full license text.
//
// spatial_BFS.cpp - Spatial analyses for binary 3D volumes, using BFS algorithm
//
// see https://www.youtube.com/watch?v=xlVX7dXLS64&t=45s for a great visual
// explanation to BFS algorithm
//
// ! Assumes all edge weights are equal in BFS  

#include "spatial_BFS.hpp"
#include <stdexcept>

std::pair<pybind11::array_t<int>, pybind11::array_t<int>>
bfs_distances(pybind11::array_t<uint8_t> volume, int x0, int y0, int z0) {

  // fast read access to the 3D numpy array
  auto accessor = volume.unchecked<3>();

  // volume size in x,y,z - cached instead of calling accessor(0), etc...
  int x_dim = accessor.shape(0);
  int y_dim = accessor.shape(1);
  int z_dim = accessor.shape(2);

  // guard if input voxels fall outside volume
  if (x0 < 0 || y0 < 0 || z0 < 0 || x0 >= x_dim || y0 >= y_dim || z0 >= z_dim)
    throw std::out_of_range("Start voxel coordinates are outside the volume");

  // flattened 1D array lookup table same size as volume
  // each entry stores index into open_voxels for that voxel
  // all at -1 initially, and stays at -1 if solid i.e. not in open_voxels
  std::vector<int> index_map(x_dim * y_dim * z_dim, -1);

  // 3d coords (x,y,z) -> single index in index_map
  // required as index_map is 1D not 3D
  auto flat = [&](int x, int y, int z) { return (x * y_dim + y) * z_dim + z; };

  // this will hold the x,y,z coordinates of every empty voxel found in the
  // volume voxel's index becomes voxel's 'id' - easier than working with coords
  std::vector<Vec3i> open_voxels;

  // loop over every voxel in the volume and only record voxels which are empty
  // (== 0)
  for (int x = 0; x < x_dim; ++x)
    for (int y = 0; y < y_dim; ++y)
      for (int z = 0; z < z_dim; ++z)
        if (accessor(x, y, z) == 0) {

          // set voxel id to next free slot in open_voxels
          // i.e. index_map id = current size of the open_voxels vector
          index_map[flat(x, y, z)] = (int)open_voxels.size();

          // now record empty voxel coordinates into open_voxels
          open_voxels.push_back({x, y, z});
        }

  const size_t n = open_voxels.size();
  int start_idx = index_map[flat(x0, y0, z0)];
  if (start_idx == -1)
    throw std::runtime_error("Start voxel is not open (0)");

  // dist[i] holds BFS distance from start voxel to open_voxels[i]
  // -1 means unreachable or not reached yet
  std::vector<int> dist(open_voxels.size(), -1); // set all open to -1

  // BFS uses a queue of ids (indices into open_voxels)
  std::queue<int> q;

  // seed the queue with the distance to start voxel
  // distance = 0 as it is distance to self
  dist[start_idx] = 0;
  q.push(start_idx);

  // 6 face neighbour directions: +-x, +-y, +-z for voxel (face-adjacent)
  // these static triples indicate possible offsets
  // TODO: change this algorithm to allow diagonal e.g Dijkstra's
  // (this would then have 26 directions)
  static const int dx[6] = {1, -1, 0, 0, 0, 0};
  static const int dy[6] = {0, 0, 1, -1, 0, 0};
  static const int dz[6] = {0, 0, 0, 0, 1, -1};

  // main BFS loop: keep 'popping' voxels off front of queue until all have been
  // explored see https://www.youtube.com/watch?v=xlVX7dXLS64&t=45s for a great
  // visual explanation to algorithm
  while (!q.empty()) {

    // take next voxel id to process and remove/pop off queue
    int cur = q.front();
    q.pop();

    // access real coords to compute neighbours
    Vec3i p = open_voxels[cur];

    // check each neighbour in the 6 faces of p
    for (int d = 0; d < 6; ++d) {
      int nx = p.x + dx[d];
      int ny = p.y + dy[d];
      int nz = p.z + dz[d];

      // skip neighbours of edge voxels on volume i.e. outside volume
      if (nx < 0 || ny < 0 || nz < 0 || nx >= x_dim || ny >= y_dim ||
          nz >= z_dim)
        continue;

      // look up this neighbours if via index_map
      int nidx = index_map[flat(nx, ny, nz)];

      // skip on two conditions:
      // nidx = -1 means neighbour is closed, skip
      // dist[nidx] != -1 means it has already been visited
      // BFS guaranteed first visit = shortest distance so gets discarded
      if (nidx == -1 || dist[nidx] != -1)
        continue;

      // this is fiurst time reaching this neighbour voxel
      // therefore distance to start voxel is +1 from the one we reached it from
      dist[nidx] = dist[cur] + 1;

      // add this neighbour to the queue so we later explore its neighbours too
      q.push(nidx);
    }
  }

  // queue is now empty so all accessible voxel distances calculated from start
  // pack open voxel coords into an N x 3 numpy array with 1D array of distances
  // to start voxel
  auto coords = pybind11::array_t<int>({(long)n, (long)3});
  auto coords_acc = coords.mutable_unchecked<2>();
  auto distances = pybind11::array_t<int>((pybind11::ssize_t)n);
  auto d_acc = distances.mutable_unchecked<1>();

  // for all open voxel coordinates:
  for (size_t i = 0; i < n; ++i) {

    // convert each back to actual coordinates
    Vec3i v = open_voxels[i];
    // add coordinates to coords via accessor
    coords_acc(i, 0) = v.x;
    coords_acc(i, 1) = v.y;
    coords_acc(i, 2) = v.z;
    d_acc(i) = dist[i]; // attach distances to the start voxel
  }

  return {coords, distances};
}

std::pair<pybind11::array_t<int>, int>
shortest_path_bfs(pybind11::array_t<uint8_t> volume, int x0, int y0, int z0,
                  int x1, int y1, int z1) {

  // fast read access to the 3D numpy array
  auto accessor = volume.unchecked<3>();

  // volume size in x,y,z - cached instead of calling accessor(0), etc...
  int x_dim = accessor.shape(0);
  int y_dim = accessor.shape(1);
  int z_dim = accessor.shape(2);

  // guard if start/end voxels fall outside volume
  if (x0 < 0 || y0 < 0 || z0 < 0 || x0 >= x_dim || y0 >= y_dim || z0 >= z_dim ||
      x1 < 0 || y1 < 0 || z1 < 0 || x1 >= x_dim || y1 >= y_dim || z1 >= z_dim)
    throw std::out_of_range("Voxel coordinates are outside the volume");

  // flattened 1D array lookup table same size as volume
  // each entry stores index into open_voxels for that voxel
  // all at -1 initially, and stays at -1 if solid i.e. not in open_voxels
  std::vector<int> index_map(x_dim * y_dim * z_dim, -1);

  // 3d coords (x,y,z) -> single index in index_map
  // required as index_map is 1D not 3D
  auto flat = [&](int x, int y, int z) { return (x * y_dim + y) * z_dim + z; };

  // this will hold the x,y,z coordinates of every empty voxel found in the
  // volume voxel's index becomes voxel's 'id' - easier than working with coords
  std::vector<Vec3i> open_voxels;

  // loop over every voxel in the volume - accessor.shape<(0,1,2)> = size of
  // volume in x,y,z axes only keep voxels which are empty (== 0)
  for (int x = 0; x < x_dim; ++x)
    for (int y = 0; y < y_dim; ++y)
      for (int z = 0; z < z_dim; ++z)
        if (accessor(x, y, z) == 0) {

          // set voxel id to next free slot in open_voxels
          // i.e. index_map id = current size of the open_voxels vector
          index_map[flat(x, y, z)] = (int)open_voxels.size();

          // now actually record empty voxel coordinates into open_voxels
          open_voxels.push_back({x, y, z});
        }

  const size_t n = open_voxels.size();
  int start_idx = index_map[flat(x0, y0, z0)];
  int end_idx = index_map[flat(x1, y1, z1)];
  if (start_idx == -1)
    throw std::runtime_error("Start voxel is not open (0)");
  if (end_idx == -1)
    throw std::runtime_error("End voxel is not open (0)");

  // dist[i] holds int BFS distance from start voxel to open_voxels[i]
  // -1 means unreachable or not reached yet
  std::vector<int> dist(open_voxels.size(), -1);
  // parent holds int voxel id of whichever voxel discovered voxel i during BFS
  std::vector<int> parent(open_voxels.size(), -1);

  // BFS uses a queue of ids (indices into open_voxels)
  std::queue<int> q;

  // seed the queue with the distance to start voxel
  // distance = 0 as it is distance to self
  dist[start_idx] = 0;
  // push into queue
  q.push(start_idx);

  // 6 face neighbour directions: +-x, +-y, +-z for voxel (face-adjacent)
  // these static triples indicate possible offsets
  // TODO: change this algorithm to allow diagonal e.g Dijkstra's
  // this would then have 26
  static const int dx[6] = {1, -1, 0, 0, 0, 0};
  static const int dy[6] = {0, 0, 1, -1, 0, 0};
  static const int dz[6] = {0, 0, 0, 0, 1, -1};

  // bool for if reached end of path
  bool found = (start_idx == end_idx);

  // main BFS loop: keep 'popping' voxels off front of queue until all have been
  // explored see https://www.youtube.com/watch?v=xlVX7dXLS64&t=45s for a great
  // visual explanation to BFS algorithm
  while (!q.empty() && !found) {

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
      if (nx < 0 || ny < 0 || nz < 0 || nx >= x_dim || ny >= y_dim ||
          nz >= z_dim)
        continue;

      // look up this neighbours if via index_map
      int nidx = index_map[flat(nx, ny, nz)];

      // skip on two conditions:
      // nidx = -1 means neighbour is closed, skip
      // dist[nidx] != -1 means it has already been visited
      // BFS guaranteed first visit = shortest distance so gets discarded
      if (nidx == -1 || dist[nidx] != -1)
        continue;

      // this is fiurst time reaching this neighbour voxel
      // therefore distance to start voxel is +1 from the one we reached it from
      dist[nidx] = dist[cur] + 1;
      parent[nidx] = cur;
      q.push(nidx);

      if (nidx == end_idx) {
        found = true;
        break; // exit BFS loop as reached end voxel
      }
    }
  }

  // case when all voxels accessible from start checked and end not reached (so
  // end_idx stays as -1)
  if (dist[end_idx] == -1)
    throw std::runtime_error("End voxel is not reachable from start voxel");

  // now there is definitely a path linking start->end so can make path ids
  // vector
  std::vector<int> path_ids;
  int cur = end_idx;

  // cur is only -1 at start voxel (as never discovered) so this retraces from
  // end voxel -> start voxel
  while (cur != -1) {
    path_ids.push_back(cur);
    // then go back a step to 'cur's parent'
    cur = parent[cur];
  }
  // for start->end
  std::reverse(path_ids.begin(), path_ids.end());

  // path has been retraced from end voxel to start voxel and reversed
  // pack path coords into an N x 3 numpy array and return this distance from
  // start <-> end
  auto path_coords = pybind11::array_t<int>({(long)path_ids.size(), (long)3});
  auto pc_acc = path_coords.mutable_unchecked<2>();

  // for every voxel on shortest path:
  for (size_t i = 0; i < path_ids.size(); ++i) {

    // convert back to actual coordinates
    Vec3i v = open_voxels[path_ids[i]];
    // write to row i of array (x,y,z columns)
    pc_acc(i, 0) = v.x;
    pc_acc(i, 1) = v.y;
    pc_acc(i, 2) = v.z;
  }

  return {path_coords, dist[end_idx]};
}