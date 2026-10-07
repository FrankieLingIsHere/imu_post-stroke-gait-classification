#pragma once
// Offline logging/type shim only. No ROS transport, clock or estimator replacement.
#include <cstdio>
#include <cstdlib>
#include <iostream>
namespace ros { class NodeHandle {}; struct Time { double value=0; double toSec() const{return value;} }; }
#define ROS_DEBUG(...) do {} while(0)
#define ROS_DEBUG_STREAM(x) do {} while(0)
#define ROS_INFO(...) do {std::fprintf(stderr,__VA_ARGS__);std::fprintf(stderr,"\n");} while(0)
#define ROS_WARN(...) ROS_INFO(__VA_ARGS__)
#define ROS_ERROR(...) ROS_INFO(__VA_ARGS__)
#define ROS_INFO_STREAM(x) do {std::cerr << x << '\n';} while(0)
#define ROS_WARN_STREAM(x) ROS_INFO_STREAM(x)
#define ROS_ERROR_STREAM(x) ROS_INFO_STREAM(x)
#define ROS_BREAK() std::abort()
