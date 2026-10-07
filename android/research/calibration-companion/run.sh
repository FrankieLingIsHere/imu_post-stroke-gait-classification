#!/bin/bash
set -euo pipefail
# ROS environment hooks intentionally read unset optional variables.
set +u
source /opt/ros/noetic/setup.bash
source /home/iKalibr/install/setup.bash
set -u
python3 /bridge/prepare.py
export ROS_MASTER_URI=http://127.0.0.1:11311 ROS_HOSTNAME=127.0.0.1
roscore >/data/roscore.log 2>&1 &
processor_master_pid=$!
trap 'kill "$processor_master_pid" 2>/dev/null || true' EXIT
sleep 2
python3 /bridge/solve.py
