// Copyright (c) 2026 Archie Benn
//
// This software is licensed under the MIT License.
// See the LICENSE file in the project root for the full license text.
//
// spatial.hpp - Declarations for spatial.cpp

#pragma once
#include <utility>
#include "common.hpp"

/**
 * @brief Computes a breadth-first search (BFS) of shortest-path distances (in voxel steps) from a start voxel 
 * to every reachable empty (0) voxel in a binary volume of solid (1) and empty (0) voxels
 *
 * Performs a 6-connected (voxel face-adjacent) BFS over all zero-valued
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
 * - dist:   (N,) int array of BFS distances, parallel to coords.
 *
 * @note Index mapping uses a flattened lookup array sized to @p volume's shape,
 * rather than a per-voxel linear search, so this runs in O(voxel count).
 */
std::pair<pybind11::array_t<int>, pybind11::array_t<int>> bfs_distances(
    pybind11::array_t<uint8_t> volume, int x0, int y0, int z0);

/**
 * @todo
 */
std::pair<pybind11::array_t<int>, int> shortest_path_bfs( pybind11::array_t<uint8_t> volume, int x0, int y0, int z0, int x1, int y1, int z1);