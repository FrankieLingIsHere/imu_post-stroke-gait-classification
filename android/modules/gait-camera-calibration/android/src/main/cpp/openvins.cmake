# Build only the pinned library. No ROS, downloaded executable, server or model.
FetchContent_Declare(openvins URL https://github.com/rpng/open_vins/archive/69488123ed9362dd44b6f28e7f4680abbff1442b.tar.gz)
FetchContent_Declare(boost URL https://archives.boost.io/release/1.84.0/source/boost_1_84_0.tar.bz2 URL_HASH SHA256=cc4b893acf645c9d4b698e9a0f08ca8846aa5d6c68275c14c3e7949c24109454)
foreach(dep openvins boost)
  FetchContent_GetProperties(${dep})
  if(NOT ${dep}_POPULATED)
    FetchContent_Populate(${dep})
  endif()
endforeach()
# The reference program terminates its process on invalid covariance/configuration.
# An embedded phone library must return that failure through JNI instead. Keep
# upstream downloads intact and apply this explicit transport patch to a build copy.
set(OV_PHONE_SOURCE "${CMAKE_CURRENT_BINARY_DIR}/phone_openvins")
include("${CMAKE_CURRENT_SOURCE_DIR}/openvins_lens_patch.cmake")
file(GLOB_RECURSE OV_PATCH_FILES RELATIVE "${openvins_SOURCE_DIR}"
  "${openvins_SOURCE_DIR}/*.h" "${openvins_SOURCE_DIR}/*.cpp")
foreach(relative ${OV_PATCH_FILES})
  file(READ "${openvins_SOURCE_DIR}/${relative}" content)
  gait_patch_fixed_lens("${relative}" "${content}" content)
  string(REPLACE "std::exit(EXIT_FAILURE);" "throw std::runtime_error(\"OpenVINS rejected estimator state\");" content "${content}")
  string(REPLACE "std::abort();" "throw std::runtime_error(\"OpenVINS rejected estimator state\");" content "${content}")
  string(REGEX REPLACE "(^|[ \t\n])assert\\(" "\\1gait_openvins_check(" content "${content}")
  if(relative STREQUAL "ov_msckf/src/core/VioManager.h")
    string(REPLACE "double initialized_time() { return startup_time; }"
      "double initialized_time() { return startup_time; }\n  void gait_begin_motion() { has_moved_since_zupt = true; params.zupt_only_at_beginning = true; }\n  void gait_end_motion() { params.zupt_only_at_beginning = false; }" content "${content}")
  endif()
  if(relative STREQUAL "ov_msckf/src/update/UpdaterZeroVelocity.cpp")
    # Small image motion alone must not override the IMU/velocity test, nor may
    # a low initial velocity override visible translation during slow walking.
    string(REPLACE "if (!disparity_passed && (chi2" "if (!disparity_passed || (chi2" content "${content}")
  endif()
  if(relative STREQUAL "ov_msckf/src/core/VioManagerHelper.cpp")
    # This transport always processes serially. Propagate initialization errors
    # back to JNI instead of letting an exception terminate a worker thread.
    string(REPLACE "std::thread thread([&] {" "auto initialize = [&] {" content "${content}")
    string(REPLACE "thread_init_running = false;\n  });" "thread_init_running = false;\n  };" content "${content}")
    string(REPLACE "if (!params.use_multi_threading_subs) {\n    thread.join();\n  } else {\n    thread.detach();\n  }"
      "initialize();" content "${content}")
  endif()
  if(relative STREQUAL "ov_msckf/src/core/VioManager.cpp")
    # Images wait for up to 200 ms of measured future IMU in our transport.
    # Preserve the initializer's older window while those readings arrive.
    # This changes retention only: no sensor observations are synthesized.
    string(REPLACE
      "message.timestamp - params.init_options.init_window_time + state->_calib_dt_CAMtoIMU->value()(0) - 0.10"
      "message.timestamp - params.init_options.init_window_time + state->_calib_dt_CAMtoIMU->value()(0) - 0.50"
      content "${content}")
  endif()
  if(relative STREQUAL "ov_init/src/init/InertialInitializer.cpp")
    # This target explicitly includes and links Ceres; upstream's generic Android
    # exclusion otherwise disables dynamic initialization despite that dependency.
    string(REPLACE "#ifndef __ANDROID__"
      "#if !defined(__ANDROID__) || defined(GAIT_ENABLE_DYNAMIC_INITIALIZER)" content "${content}")
  endif()
  get_filename_component(parent "${OV_PHONE_SOURCE}/${relative}" DIRECTORY)
  file(MAKE_DIRECTORY "${parent}")
  set(patched "#include \"openvins_assert.h\"\n${content}")
  set(previous "")
  if(EXISTS "${OV_PHONE_SOURCE}/${relative}")
    file(READ "${OV_PHONE_SOURCE}/${relative}" previous)
  endif()
  if(NOT previous STREQUAL patched)
    file(WRITE "${OV_PHONE_SOURCE}/${relative}" "${patched}")
  endif()
endforeach()
set(openvins_SOURCE_DIR "${OV_PHONE_SOURCE}")
file(GLOB BOOST_FILESYSTEM ${boost_SOURCE_DIR}/libs/filesystem/src/*.cpp)
add_library(gait_boost_filesystem STATIC ${BOOST_FILESYSTEM})
target_include_directories(gait_boost_filesystem PUBLIC ${boost_SOURCE_DIR})
target_compile_definitions(gait_boost_filesystem PRIVATE BOOST_FILESYSTEM_SOURCE BOOST_FILESYSTEM_STATIC_LINK BOOST_FILESYSTEM_NO_CXX20_ATOMIC_REF)
file(GLOB_RECURSE OV_CORE ${openvins_SOURCE_DIR}/ov_core/src/*.cpp)
file(GLOB_RECURSE OV_INIT ${openvins_SOURCE_DIR}/ov_init/src/*.cpp)
list(FILTER OV_CORE EXCLUDE REGEX ".*/test_[^/]*\\.cpp$")
list(FILTER OV_INIT EXCLUDE REGEX ".*/(test_[^/]*|SimulatorInit)\\.cpp$")
set(OV_MS ${openvins_SOURCE_DIR}/ov_msckf/src)
add_library(gait_openvins SHARED openvins_engine.cpp ${OV_CORE} ${OV_INIT}
  ${OV_MS}/state/State.cpp ${OV_MS}/state/StateHelper.cpp ${OV_MS}/state/Propagator.cpp
  ${OV_MS}/core/VioManager.cpp ${OV_MS}/core/VioManagerHelper.cpp
  ${OV_MS}/update/UpdaterHelper.cpp ${OV_MS}/update/UpdaterMSCKF.cpp
  ${OV_MS}/update/UpdaterSLAM.cpp ${OV_MS}/update/UpdaterZeroVelocity.cpp)
target_include_directories(gait_openvins PRIVATE ${OV_MS} ${openvins_SOURCE_DIR}/ov_core/src ${openvins_SOURCE_DIR}/ov_init/src
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${eigen_SOURCE_DIR} ${ceres_SOURCE_DIR}/include ${ceres_BINARY_DIR}/config ${ceres_SOURCE_DIR}/internal/ceres/miniglog)
target_compile_definitions(gait_openvins PRIVATE ROS_AVAILABLE=0 ENABLE_ARUCO_TAGS=0 BOOST_FILESYSTEM_STATIC_LINK GAIT_ENABLE_DYNAMIC_INITIALIZER=1)
target_link_libraries(gait_openvins PRIVATE gait_boost_filesystem ceres OpenCV::opencv_java4 log)
