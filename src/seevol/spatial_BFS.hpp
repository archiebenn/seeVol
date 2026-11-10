// Copyright (c) 2026 Archie Benn
//
// This software is licensed under the MIT License.
// See the LICENSE file in the project root for the full license text.
//
// spatial_BFS.hpp - Declarations for spatial_BFS.cpp

#pragma once
#include "common.hpp"
#include <utility>

// Computes a breadth-first search (BFS) of distances (in voxel steps) from a
// start voxel to every reachable empty (0) voxel in a binary 3D volume of solid
// ! Assumes all edge weights are equal
// (1) and empty (0) voxels
// Accepts:
// - volume (read-only view of the 3D uint8 numpy array)
// - x0, y0, z0 (start voxel coordinates)
// Returns:
// - Nx3 array of open voxel coordinates
// - 1D array of distances to each from the start voxel
std::pair<pybind11::array_t<int>, pybind11::array_t<int>>
bfs_distances(pybind11::array_t<uint8_t> volume, int x0, int y0, int z0);

// Computes a breadth-first search (BFS) to get shortest-path from a start voxel
// to end voxel
// ! Assumes all edge weights are equal
// Accepts:
// - volume (read-only view of the 3D uint8 numpy array)
// - x0, y0, z0 (start voxel coordinates)
// - x1, y1, z1 (end voxel coordinates)
// Returns:
// - Nx3 array of shortest-path voxel coordinates
// - single int value of this distance in voxel steps
std::pair<pybind11::array_t<int>, int>
shortest_path_bfs(pybind11::array_t<uint8_t> volume, int x0, int y0, int z0,
                  int x1, int y1, int z1);