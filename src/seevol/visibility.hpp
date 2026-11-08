// Copyright (c) 2026 Archie Benn
//
// This software is licensed under the MIT License.
// See the LICENSE file in the project root for the full license text.
//
//visibility.hpp - Declarations for visibility.cpp

#pragma once
#include <utility>
#include "common.hpp"


/**
 * @brief Return voxel value (0 or 1) from numpy array (3D volume)
 * For testing C++ <-> Python indexing  
 *
 * @param volume numpy 3D uint8 array data type
 * @param x voxel index along the x axis
 * @param y voxel index along the y axis
 * @param z voxel index along the z axis
 * @return byte value of voxel from coordinates  
 */
uint8_t get_voxel_value(pybind11::array_t<uint8_t> volume, int x, int y, int z);


/**
 * @brief Return if a **single** pair of voxels is visible to each other in a straight line without being occluded by a solid/1 voxel
 * Using "Amanatides, J. & Woo, A. A Fast Voxel Traversal Algorithm for Ray Tracing." algorithm  
 *
 * @param volume read-only view of the 3D uint8 numpy array
 * @param x0 start voxel index along the x axis
 * @param y0 start voxel index along the y axis
 * @param z0 start voxel index along the z axis
 * @param x1 end voxel index along the x axis
 * @param y1 end voxel index along the y axis
 * @param z1 end voxel index along the z axis
 * @return BOOL for whether visible in line or sight (true) or not (false)    
 */
bool is_visible(const Vol& volume, int x0, int y0, int z0, int x1, int y1, int z1);


// for python import after changing the parameters for main is_visible
bool is_visible_py(pybind11::array_t<uint8_t> volume, int x0, int y0, int z0, int x1, int y1, int z1);


/**
 * @brief Compute all visible pairs of empty (0) voxels in the volume for visibility graph analysis.
 * One call from Python; returns the empty voxel coordinates plus the list of visible (i, j) index pairs into that array.
 *
 * @param volume numpy 3D uint8 array data type
 * @return pair of: 
 * - N x 3 int array of empty voxel coordinates
 * - M x 2 int array of visible index pairs
 */
std::pair<pybind11::array_t<int>, pybind11::array_t<int>> visibility_graph(pybind11::array_t<uint8_t> volume, bool verbose);


/**
 * @brief Compute visibility scores for all empty (0) voxels in the volume.
 * Similar to visible_pairs but does not store edges: only keeps raw scores per voxel so less memory heavy.  
 * One call from Python; returns the empty voxel coordinates plus the visibility score.
 *
 * @param volume numpy 3D uint8 array data type
 * @return pair of: 
 * - N x 3 int array of empty voxel coordinates
 * - N visibility scores
 */
std::pair<pybind11::array_t<int>, pybind11::array_t<int>> visibility_scores(pybind11::array_t<uint8_t> volume, bool verbose);