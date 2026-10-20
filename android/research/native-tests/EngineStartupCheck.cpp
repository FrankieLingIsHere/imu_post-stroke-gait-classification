// Exercise the actual production Engine constructor and motion transitions.
#define GAIT_OPENVINS_HOST
#define GAIT_OPENVINS_NO_MAIN
#include "openvins_engine.cpp"
#include <iostream>
void require(bool yes){if(!yes)throw std::runtime_error("Startup configuration contract failed");}
int main(int argc,char** argv){try{
 require(argc==3);
 {
  gait::Engine engine(argv[1]);auto p=engine.vio->get_params();
  require(engine.calibrating&&!p.init_options.init_dyn_use&&!p.init_options.init_dyn_mle_opt_calib);
  require(p.init_options.sigma_a==p.imu_noises.sigma_a&&p.init_options.sigma_w==p.imu_noises.sigma_w);
  require(p.init_options.sigma_ab==p.imu_noises.sigma_ab&&p.init_options.sigma_wb==p.imu_noises.sigma_wb);
  require(p.try_zupt&&!p.zupt_only_at_beginning);
  engine.beginMotion();require(engine.vio->get_params().zupt_only_at_beginning);
  engine.endMotion();require(!engine.vio->get_params().zupt_only_at_beginning);
 }
 {
  gait::Engine engine(argv[2]);auto p=engine.vio->get_params();
  require(!engine.calibrating&&p.init_options.init_dyn_use&&!p.init_options.init_dyn_mle_opt_calib);
  require(engine.fullReferenceLens&&p.camera_intrinsics.at(0)->fixed_radial_k3()==engine.fixedLensK3);
  require(p.init_options.sigma_a==p.imu_noises.sigma_a&&p.init_options.sigma_w==p.imu_noises.sigma_w);
 }
 std::cout<<"PASS: actual Engine quiet-first setup, matching initializer noise, consistent geometry, full reference lens and walking/end transitions.\n";
 return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
