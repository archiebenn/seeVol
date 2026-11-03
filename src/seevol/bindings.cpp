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
      "Computes all visible voxel pairs in a volume and returns Nx3 int array of open voxel coordinates as well a linked Mx2 array of visible index pairs");
}