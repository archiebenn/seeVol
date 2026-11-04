/* 
spatial.hpp - declarations for spatial.cpp
*/  

#pragma once
#include <utility>
#include "common.hpp"

/**
 * @brief Compute breadth-first search (BFS) shortest-path distances (in voxel steps) from a start voxel 
 * to every reachable open voxel in a binary volume of closed (0) open (1) voxels
 *
 * Performs a 6-connected (face-adjacent) breadth-first search over all nonzero
 * voxels in @p volume, starting at (@p x0, @p y0, @p z0).
 * 
 * https://www.youtube.com/watch?v=xlVX7dXLS64&t=45s provides a good background to BFS  
 *
 * @param volume  numpy 3D uint8 array data type  
 * @param x0      start voxel x coordinate.
 * @param y0      start voxel y coordinate.
 * @param z0      start voxel z coordinate.
 *
 * @return A pair of numpy arrays:
 * - coords: (N, 3) int array of open voxel coordinates.
 * - dist:   (N,) int array of BFS distances, parallel to @p coords.
 *
 * @throws std::out_of_range if the start voxel is outside the volume.
 * @throws std::runtime_error if the start voxel is not open.
 *
 * @note Index mapping uses a flattened lookup array sized to @p volume's shape,
 * rather than a per-voxel linear search, so this runs in O(voxel count).
 */
std::pair<pybind11::array_t<int>, pybind11::array_t<int>> bfs_distances(
    pybind11::array_t<uint8_t> volume, int x0, int y0, int z0);