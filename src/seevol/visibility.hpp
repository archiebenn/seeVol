// Copyright (c) 2026 Archie Benn
//
// This software is licensed under the MIT License.
// See the LICENSE file in the project root for the full license text.
//
// visibility.hpp - Declarations for visibility.cpp

#pragma once
#include "common.hpp"
#include <utility>

// For testing C++ <-> Python indexing
// Accepts: 
// - x, y, z (voxel coordinates)  
// Return: 
// - voxel value (0 or 1) from numpy array (3D volume)
uint8_t get_voxel_value(pybind11::array_t<uint8_t> volume, int x, int y, int z);


// Check if a single pair of voxels is visible to each other in a
// straight line without being occluded by a solid/1 voxel Using "Amanatides, J.
// & Woo, A. A Fast Voxel Traversal Algorithm for Ray Tracing." algorithm
// Accepts: 
// - volume (read-only view of the 3D uint8 numpy array)
// - x0, y0, z0 (start voxel coordinates)
// - x1, y1, z1 (end voxel coordinates)  
// Returns: 
// - BOOL (whether line of sight is possible or not)  
bool is_visible(const Vol &volume, int x0, int y0, int z0, int x1, int y1,
                int z1);

// for python import after changing the parameters for the above is_visible
bool is_visible_py(pybind11::array_t<uint8_t> volume, int x0, int y0, int z0,
                   int x1, int y1, int z1);

// Computes all visible pairs of empty (0) voxels in the volume for
// visibility graph analysis (Runs at O(n_open_voxels**2))  
// Accepts: 
// - volume (read-only view of the 3D uint8 numpy array)
// - BOOL verbose (True for output during ray casting)
// Returns:
// - Nx3 array of all empty voxel coordinates (nodes) 
// - Mx2 array of visible (i, j) index pairs (edges) into that array  
std::pair<pybind11::array_t<int>, pybind11::array_t<int>>
visibility_graph(pybind11::array_t<uint8_t> volume, bool verbose);

// Compute visibility scores for all empty (0) voxels in the volume.
// Similar to visibility_graph() but does not store edges: only keeps raw scores per
// voxel so less memory heavy
// Accepts: 
// volume - read-only view of the 3D uint8 numpy array
// - BOOL verbose (True for output during ray casting)
// Returns:
// - Nx3 array of empty voxel coordinates in the volume
// - N visibility scores
std::pair<pybind11::array_t<int>, pybind11::array_t<int>>
visibility_scores(pybind11::array_t<uint8_t> volume, bool verbose);