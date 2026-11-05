cmake_minimum_required(VERSION 3.15)
project(seevol)

# C++ 17 standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# require pybind  
find_package(pybind11 REQUIRED)

# create module from every .cpp file
pybind11_add_module(voxel_cpp 
                    src/seevol/visibility.cpp 
                    src/seevol/spatial.cpp 
                    src/seevol/bindings.cpp)

# for multi-threading the hot loop in is_visible:
# macOS: auto-locate Homebrew's libomp (no-op elsewhere)
if(APPLE)
    execute_process(COMMAND brew --prefix libomp
                    OUTPUT_VARIABLE HOMEBREW_LIBOMP
                    OUTPUT_STRIP_TRAILING_WHITESPACE
                    ERROR_QUIET)
    if(HOMEBREW_LIBOMP)
        list(APPEND CMAKE_PREFIX_PATH "${HOMEBREW_LIBOMP}")
    endif()
endif()
find_package(OpenMP)
if(OpenMP_CXX_FOUND)
    target_link_libraries(voxel_cpp PRIVATE OpenMP::OpenMP_CXX)
else()
    message(WARNING "OpenMP not found: building serial (non-threaded and slower) version. Please install!")
endif()

# once compiled so an .so, add to the seevol package folder  
install(TARGETS voxel_cpp DESTINATION seevol)