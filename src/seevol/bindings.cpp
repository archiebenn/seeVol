// Copyright (c) 2026 Archie Benn
//
// This software is licensed under the MIT License.
// See the LICENSE file in the project root for the full license text.
//
// bindings.cpp - Pybind module for seeVol python access  


#include "common.hpp"
#include "visibility.hpp"
#include "spatial.hpp"

PYBIND11_MODULE(voxel_cpp, m) {
    m.def("get_voxel_value", &get_voxel_value, "Return voxel value (0 or 1) from numpy array (3D volume)");

    m.def("is_visible", &is_visible_py, "Return whether a single voxel pair has line of sight");

    m.def("visibility_graph", &visibility_graph, 
      pybind11::arg("volume"),
      pybind11::arg("verbose") = false,
      "Computes all visible empty (0) voxel pairs in a volume. Returns Nx3 int array of empty voxel coordinates (nodes) alongside a linked Mx2 array of visible index pairs (edges)");

    m.def("visibility_scores", &visibility_scores, 
      pybind11::arg("volume"),
      pybind11::arg("verbose") = false,
      "Computes visibility scores for all empty (0) voxels in a volume. Returns Nx3 int array of empty voxel coordinates and n visibility scores.");

      m.def("bfs_distances", &bfs_distances,
        pybind11::arg("volume"),
        pybind11::arg("x0"),
        pybind11::arg("y0"),
        pybind11::arg("z0"),
        "Compute spatial BFS distances from an input voxel (x0, y0, z0) to all other open voxels from 3D numpy array volume");

        m.def("shortest_path_bfs", &shortest_path_bfs,
        pybind11::arg("volume"),
        pybind11::arg("x0"),
        pybind11::arg("y0"),
        pybind11::arg("z0"),
        pybind11::arg("x1"),
        pybind11::arg("y1"),
        pybind11::arg("z1"),
        "Compute spatial BFS shortes distance from a start voxel (x0, y0, z0) to an end voxel (x1, y1, z1) in a 3D numpy array volume");
}