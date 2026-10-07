cmake_minimum_required(VERSION 3.19)
project(gaittrace_vins_reference LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT VINS_SOURCE)
  message(FATAL_ERROR "Set VINS_SOURCE to pinned upstream VINS-Mono checkout")
endif()
execute_process(COMMAND git -C ${VINS_SOURCE} rev-parse HEAD
  OUTPUT_VARIABLE VINS_COMMIT OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ERROR_IS_FATAL ANY)
if(NOT VINS_COMMIT STREQUAL "90dabb5ec79946ae42fd2e1e91d4e69aabe1e25d")
  message(FATAL_ERROR "VINS_SOURCE must match reviewed upstream commit, got ${VINS_COMMIT}")
endif()
execute_process(COMMAND git -C ${VINS_SOURCE} diff --quiet HEAD -- vins_estimator
  RESULT_VARIABLE VINS_MODIFIED)
if(NOT VINS_MODIFIED EQUAL 0)
  message(FATAL_ERROR "Upstream estimator sources must remain unchanged")
endif()
find_package(OpenCV REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(Ceres 1.14.0 EXACT REQUIRED)
set(VS ${VINS_SOURCE}/vins_estimator/src)
add_executable(vins_reference
  replay.cpp
  ${VS}/estimator.cpp ${VS}/feature_manager.cpp
  ${VS}/factor/pose_local_parameterization.cpp
  ${VS}/factor/projection_factor.cpp ${VS}/factor/projection_td_factor.cpp
  ${VS}/factor/marginalization_factor.cpp ${VS}/utility/utility.cpp
  ${VS}/initial/solve_5pts.cpp ${VS}/initial/initial_aligment.cpp
  ${VS}/initial/initial_sfm.cpp ${VS}/initial/initial_ex_rotation.cpp)
target_include_directories(vins_reference PRIVATE ${CMAKE_CURRENT_SOURCE_DIR} ${VS} ${OpenCV_INCLUDE_DIRS} ${CERES_INCLUDE_DIRS})
target_compile_options(vins_reference PRIVATE -include ${CMAKE_CURRENT_SOURCE_DIR}/compat.h)
target_link_libraries(vins_reference PRIVATE Eigen3::Eigen ${OpenCV_LIBS} ${CERES_LIBRARIES} pthread)
