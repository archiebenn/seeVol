/*
common.hpp - shared helpers for seevol
*/

#pragma once
#include <cstdint>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

// 2 structs: 3d integer and 3d double
struct Vec3i {int x, y, z;};
struct Vec3d {double x, y, z;};

// type alias for the volume. unchecked_reference gives access to underlying array in Python so doesn't need to load it 
// i.e. gives raw view to the numpy array   
// making this alias and passing by reference in is_visible stops accessor being rebuilt on every is_visible loop
using Vol = pybind11::detail::unchecked_reference<uint8_t, 3>;

