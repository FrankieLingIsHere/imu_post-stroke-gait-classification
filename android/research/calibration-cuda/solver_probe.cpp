// A synthetic known-answer CUDA linear-solver check, not a phone calibration.
#include <ceres/ceres.h>
#include <cuda_runtime_api.h>
#include <cmath>
#include <iostream>

struct Observation {
  explicit Observation(double observed) : observed(observed) {}
  template <typename T> bool operator()(const T* value, const T* local, T* residual) const {
    residual[0] = value[0] + local[0] - T(observed);
    return true;
  }
  double observed;
};

struct Anchor {
  template <typename T> bool operator()(const T* local, T* residual) const {
    residual[0] = local[0];
    return true;
  }
};

int main(int argc, char** argv) {
  const bool gpu = argc == 2 && std::string(argv[1]) == "cuda";
  int count = 0;
  if (gpu && (cudaGetDeviceCount(&count) != cudaSuccess || count < 1)) return 2;
  if (gpu) {
    cudaDeviceProp properties;
    if (cudaGetDeviceProperties(&properties, 0) != cudaSuccess) return 3;
    std::cout << "CUDA device: " << properties.name << std::endl;
  }
  if (!ceres::IsDenseLinearAlgebraLibraryTypeAvailable(gpu ? ceres::CUDA : ceres::EIGEN)) return 4;
  double value = 0;
  double local[128] = {};
  ceres::Problem problem;
  auto ordering = std::make_shared<ceres::ParameterBlockOrdering>();
  for (int i = 0; i < 128; ++i) {
    for (int j = 0; j < 16; ++j)
      problem.AddResidualBlock(new ceres::AutoDiffCostFunction<Observation, 1, 1, 1>(
        new Observation(2.5)), nullptr, &value, &local[i]);
    problem.AddResidualBlock(new ceres::AutoDiffCostFunction<Anchor, 1, 1>(
      new Anchor), nullptr, &local[i]);
    ordering->AddElementToGroup(&local[i], 0);
  }
  // Keep a real nonempty reduced system for CUDA's dense Schur factorization.
  ordering->AddElementToGroup(&value, 1);
  ceres::Solver::Options options;
  options.linear_solver_type = ceres::DENSE_SCHUR;
  options.dense_linear_algebra_library_type = gpu ? ceres::CUDA : ceres::EIGEN;
  options.trust_region_strategy_type = ceres::DOGLEG;
  options.num_threads = 2;
  options.linear_solver_ordering = ordering;
  ceres::Solver::Summary summary;
  ceres::Solve(options, &problem, &summary);
  if (gpu && cudaDeviceSynchronize() != cudaSuccess) return 5;
  std::cout << summary.FullReport() << "\nKnown answer: " << value << std::endl;
  bool correct = summary.IsSolutionUsable() && std::abs(value - 2.5) < 1e-7;
  for (double nuisance : local) correct = correct && std::abs(nuisance) < 1e-7;
  return correct ? 0 : 6;
}
