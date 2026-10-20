# Experimental calibration build. The production reference image stays intact.
# CUDA 12.9.1 devel Ubuntu 22.04, already verified for the RTX 5060 frontend.
FROM nvidia/cuda@sha256:020bc241a628776338f4d4053fed4c38f6f7f3d7eb5919fecb8de313bb8ba47c AS toolkit
FROM gaittrace-ikalibr:reference-v1 AS ceres
COPY --from=toolkit /usr/local/cuda-12.9 /usr/local/cuda-12.9
ENV PATH=/usr/local/cuda-12.9/bin:${PATH}
ENV LD_LIBRARY_PATH=/usr/local/cuda-12.9/lib64:${LD_LIBRARY_PATH}
# Rebuild the exact unmodified Ceres source shipped with the authors' image.
# Ceres 2.2 uses USE_CUDA, not the newer WITH_CUDA configuration flag.
RUN nvcc --version && \
    test "$(git -C /home/software/ceres-solver rev-parse HEAD)" = 85331393dc0dff09f6fb9903ab0c4bfa3e134b01 && \
    git -C /home/software/ceres-solver diff --quiet HEAD && \
    cmake -S /home/software/ceres-solver -B /opt/ceres-cuda-build \
      -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/ceres-cuda \
      -DUSE_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=120 \
      -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF -DBUILD_BENCHMARKS=OFF \
      -DBUILD_SHARED_LIBS=ON && \
    cmake --build /opt/ceres-cuda-build --parallel 2 && \
    cmake --install /opt/ceres-cuda-build && \
    grep 'CUDA' /opt/ceres-cuda/lib/cmake/Ceres/CeresConfig.cmake

FROM ceres AS probe
COPY CMakeLists.txt solver_probe.cpp /opt/probe-src/
RUN cmake -S /opt/probe-src -B /opt/probe-build \
      -DCeres_DIR=/opt/ceres-cuda/lib/cmake/Ceres && \
    cmake --build /opt/probe-build --parallel 2

# authors-source.tar is generated locally with recover_sources.py. Do not commit
# the archive, dependency tree, binary libraries or resulting Docker images.
FROM probe AS solver
ADD authors-source.tar /
COPY source-provenance.json /opt/source-provenance.json
COPY build_includes.py /opt/build_includes.py
RUN test "$(git -C /home/iKalibr/src/ikalibr rev-parse HEAD)" = 1fd2b88853ac2798c926c48cdd5b86fda15fde9d && \
    test "$(git -C /home/iKalibr/src/ikalibr/thirdparty/ctraj rev-parse HEAD)" = 48d5bc7b2dc144cd35f8b31100a8c3db0d6353c5 && \
    test "$(git -C /home/iKalibr/src/ikalibr/thirdparty/veta rev-parse HEAD)" = 8097ba552ee797b22727b7963930458d6f27c073 && \
    cmake -S /home/iKalibr/src/ikalibr/thirdparty/ctraj -B /opt/ctraj-cuda-build \
      -DCeres_DIR=/opt/ceres-cuda/lib/cmake/Ceres \
      -DCMAKE_INSTALL_PREFIX=/home/iKalibr/src/ikalibr/thirdparty/ctraj-install && \
    cmake --build /opt/ctraj-cuda-build --target ctraj --parallel 1 && \
    cmake --install /opt/ctraj-cuda-build
# The upstream unity build supplies declarations through neighboring sources.
# Non-unity compilation needs explicit headers/linkage; function bodies stay intact.
RUN python3 /opt/build_includes.py /home/iKalibr/src/ikalibr && \
    bash -c 'source /opt/ros/noetic/setup.bash && \
    cmake -S /home/iKalibr/src/ikalibr -B /opt/ikalibr-cuda-build \
      -DCeres_DIR=/opt/ceres-cuda/lib/cmake/Ceres -DUSE_CMAKE_UNITY_BUILD=OFF \
      -DCATKIN_DEVEL_PREFIX=/opt/ikalibr-cuda-devel \
      -DPYTHON_EXECUTABLE=/usr/bin/python3 && \
    cmake --build /opt/ikalibr-cuda-build --target ikalibr_generate_messages --parallel 1 && \
    cmake --build /opt/ikalibr-cuda-build --target ikalibr_prog --parallel 2'
ENV LD_LIBRARY_PATH=/opt/ceres-cuda/lib:/opt/ikalibr-cuda-devel/lib:/home/iKalibr/src/ikalibr/thirdparty/ctraj-install/lib:/usr/local/cuda-12.9/lib64:${LD_LIBRARY_PATH}
