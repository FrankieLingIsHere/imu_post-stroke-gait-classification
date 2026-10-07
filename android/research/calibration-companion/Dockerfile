# Official iKalibr environment, pinned to the inspected publication authors' image.
FROM ulong2/ie_kalibr_image@sha256:2de8ac994a86951b6255e4b8485eae9982ea3ed03bac33dd9d0ee254e383587c
# ROS Noetic is already installed in this snapshot. Its expired apt signing key
# must not lead to disabling signature checks; only Ubuntu packages are needed.
RUN sed -i '/packages.ros.org/d' /etc/apt/sources.list.d/*.list && apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends xvfb xauth && rm -rf /var/lib/apt/lists/*
ENV LIBGL_ALWAYS_SOFTWARE=1 QT_QPA_PLATFORM=offscreen
WORKDIR /data
ENTRYPOINT ["bash", "/bridge/run.sh"]
