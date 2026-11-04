/*
bindings.cpp - pybind module for python access (voxel_cpp must match name in CMakeLists.txt)  
*/

#include "common.hpp"
#include "visibility.hpp"

PYBIND11_MODULE(voxel_cpp, m) {
    m.def("get_voxel_value", &get_voxel_value, "Return voxel value (0 or 1) from numpy array (3D volume)");
    m.def("is_visible", &is_visible_py, "Return whether a single voxel pair has line of sight");
    m.def("visible_pairs", &visible_pairs, 
      pybind11::arg("volume"),
      pybind11::arg("verbose") = false,
      "Computes all visible open voxel pairs in a volume. Returns Nx3 int array of open voxel coordinates (nodes) alongside a linked Mx2 array of visible index pairs (edges)");
    m.def("visibility_scores", &visibility_scores, 
      pybind11::arg("volume"),
      pybind11::arg("verbose") = false,
      "Computes visibility scores for all open voxels in a volume. Returns Nx3 int array of open voxel coordinates and n visibility scores.");
}