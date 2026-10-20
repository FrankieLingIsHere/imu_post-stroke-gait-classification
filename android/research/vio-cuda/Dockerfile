# Isolated CUDA frontend: keep the Windows calibration OpenCV installation intact.
FROM nvidia/cuda@sha256:020bc241a628776338f4d4053fed4c38f6f7f3d7eb5919fecb8de313bb8ba47c
ARG OPENCV_VERSION=4.12.0
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates git cmake ninja-build g++ python3-dev python3-numpy \
    libjpeg-dev libpng-dev && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 --branch ${OPENCV_VERSION} https://github.com/opencv/opencv.git /src/opencv && \
    git clone --depth 1 --branch ${OPENCV_VERSION} https://github.com/opencv/opencv_contrib.git /src/opencv_contrib && \
    test "$(git -C /src/opencv rev-parse HEAD)" = 49486f61fb25722cbcf586b7f4320921d46fb38e && \
    test "$(git -C /src/opencv_contrib rev-parse HEAD)" = d943e1d61c8bc556a13783e1546ee7c1a9e0b1cf && \
    git -C /src/opencv rev-parse HEAD > /opt/opencv-source.txt && \
    git -C /src/opencv_contrib rev-parse HEAD >> /opt/opencv-source.txt
RUN cmake -S /src/opencv -B /src/build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/opencv \
    -DOPENCV_EXTRA_MODULES_PATH=/src/opencv_contrib/modules \
    -DBUILD_LIST=core,imgproc,imgcodecs,calib3d,video,cudev,cudaarithm,cudafilters,cudaimgproc,cudawarping,cudaoptflow,python3 \
    -DWITH_CUDA=ON -DCUDA_ARCH_BIN=12.0 -DCUDA_ARCH_PTX= \
    -DWITH_CUDNN=OFF -DOPENCV_DNN_CUDA=OFF -DBUILD_opencv_cudacodec=OFF \
    -DBUILD_TESTS=OFF -DBUILD_PERF_TESTS=OFF -DBUILD_EXAMPLES=OFF \
    -DWITH_FFMPEG=OFF -DWITH_GSTREAMER=OFF -DWITH_GTK=OFF -DWITH_QT=OFF \
    -DPYTHON3_EXECUTABLE=/usr/bin/python3 -DPYTHON3_PACKAGES_PATH=/opt/opencv/lib/python3.12/site-packages && \
    cmake --build /src/build --parallel 8 && cmake --install /src/build && \
    rm -rf /src
ENV PYTHONPATH=/opt/opencv/lib/python3.12/site-packages
ENV LD_LIBRARY_PATH=/opt/opencv/lib:/usr/local/cuda/lib64
ARG GAITTRACE_RECIPE_SHA256=unrecorded
LABEL org.gaittrace.cuda-recipe-sha256=${GAITTRACE_RECIPE_SHA256}
WORKDIR /data
ENTRYPOINT ["python3"]
