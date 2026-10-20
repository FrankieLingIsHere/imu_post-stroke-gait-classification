cmake_minimum_required(VERSION 3.22.1)
project(gait_phone_vio LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
include(FetchContent)
# Immutable upstream commits. Dependencies stay in the generated build directory.
FetchContent_Declare(eigen URL https://github.com/eigenteam/eigen-git-mirror/archive/36b95962756c1fce8e29b1f8bc45967f30773c00.tar.gz)
FetchContent_Declare(ceres URL https://github.com/ceres-solver/ceres-solver/archive/facb199f3eda902360f9e1d5271372b7e54febe1.tar.gz)
FetchContent_Declare(vins URL https://github.com/HKUST-Aerial-Robotics/VINS-Mono/archive/90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d.tar.gz)
foreach(dep eigen ceres vins)
  FetchContent_GetProperties(${dep})
  if(NOT ${dep}_POPULATED)
    FetchContent_Populate(${dep})
  endif()
endforeach()
file(COPY ${eigen_SOURCE_DIR}/Eigen DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/include/eigen3)
set(EIGEN_INCLUDE_DIR ${eigen_SOURCE_DIR} CACHE PATH "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(MINIGLOG ON CACHE BOOL "" FORCE)
set(GFLAGS OFF CACHE BOOL "" FORCE)
set(SUITESPARSE OFF CACHE BOOL "" FORCE)
set(CXSPARSE OFF CACHE BOOL "" FORCE)
set(LAPACK OFF CACHE BOOL "" FORCE)
set(OPENMP OFF CACHE BOOL "" FORCE)
set(CXX11 ON CACHE BOOL "" FORCE)
add_compile_options("SHELL:-include limits")
add_subdirectory(${ceres_SOURCE_DIR} ${ceres_BINARY_DIR} EXCLUDE_FROM_ALL)
find_package(OpenCV REQUIRED CONFIG)
set(VS ${vins_SOURCE_DIR}/vins_estimator/src)
set(REFERENCE ${CMAKE_CURRENT_SOURCE_DIR}/../../../../../../research/vio-reference)
add_library(gait_phone_vio SHARED phone_vio.cpp
  ${VS}/estimator.cpp ${VS}/feature_manager.cpp
  ${VS}/factor/pose_local_parameterization.cpp ${VS}/factor/projection_factor.cpp
  ${VS}/factor/projection_td_factor.cpp ${VS}/factor/marginalization_factor.cpp
  ${VS}/utility/utility.cpp ${VS}/initial/solve_5pts.cpp
  ${VS}/initial/initial_aligment.cpp ${VS}/initial/initial_sfm.cpp
  ${VS}/initial/initial_ex_rotation.cpp)
target_include_directories(gait_phone_vio PRIVATE ${REFERENCE} ${VS} ${CMAKE_CURRENT_BINARY_DIR}/include
  ${eigen_SOURCE_DIR} ${ceres_SOURCE_DIR}/include ${ceres_BINARY_DIR}/config
  ${ceres_SOURCE_DIR}/internal/ceres/miniglog)
target_compile_options(gait_phone_vio PRIVATE "SHELL:-include \"${CMAKE_CURRENT_SOURCE_DIR}/android_compat.h\"")
target_link_libraries(gait_phone_vio PRIVATE ceres OpenCV::opencv_java4 log)
include(openvins.cmake)
