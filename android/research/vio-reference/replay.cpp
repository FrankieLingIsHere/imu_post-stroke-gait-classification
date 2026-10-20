// Offline wrapper around pinned, unchanged upstream estimator sources.
// No clinical readiness. Supplied noise/translation guesses are recorded by Python.
#include "estimator.h"
#include "fixed_time_observation.h"
#include <algorithm>
#include <iomanip>
#include <sstream>
#include <cstring>
#include <new>

double INIT_DEPTH=5, MIN_PARALLAX=10.0/460;
double ACC_N=.08, ACC_W=.00004, GYR_N=.004, GYR_W=.000002;
std::vector<Eigen::Matrix3d> RIC;
std::vector<Eigen::Vector3d> TIC;
Eigen::Vector3d G(0,0,9.80665);
double BIAS_ACC_THRESHOLD=.1, BIAS_GYR_THRESHOLD=.1;
double SOLVER_TIME=.2;
int NUM_ITERATIONS=8, ESTIMATE_EXTRINSIC=1, ESTIMATE_TD=1, ROLLING_SHUTTER=1;
std::string EX_CALIB_RESULT_PATH, VINS_RESULT_PATH, IMU_TOPIC="/imu0";
double ROW=480, COL=640, TD=0, TR=0;

struct Imu {double t; Eigen::Vector3d a,g;};
using Features=std::map<int,std::vector<std::pair<int,Eigen::Matrix<double,7,1>>>>;
std::vector<double> split(const std::string& line){
  std::stringstream s(line);std::string part;std::vector<double> result;
  while(std::getline(s,part,','))result.push_back(std::stod(part));
  return result;
}

int main(int argc,char** argv){
  if(argc==2 && std::string(argv[1])=="--capabilities"){
    std::cout<<"{\"distanceProtocolVersion\":2,\"fixedGeometry\":true,\"fixedTimeOffset\":true,\"fixedTimeRowCorrection\":true,\"replayInitializationWindow\":true}\n";return 0;
  }
  if(argc<2 || argc>3){std::cerr<<"Usage: vins_reference INPUT_DIRECTORY [OUTPUT_PREFIX]\n";return 2;}
  std::string directory=argv[1];
  std::string prefix=argc==3 ? argv[2] : "reference";
  if(prefix.find_first_not_of("abcdefghijklmnopqrstuvwxyz0123456789-_")!=std::string::npos)return 2;
  cv::FileStorage config(directory+"/reference.yaml",cv::FileStorage::READ);
  if(!config.isOpened())return 3;
  cv::Mat r,t;
  config["extrinsicRotation"]>>r; config["extrinsicTranslation"]>>t;
  Eigen::Matrix3d rotation; Eigen::Vector3d translation;
  cv::cv2eigen(r,rotation);cv::cv2eigen(t,translation);
  RIC.push_back(rotation);TIC.push_back(translation);
  config["td"]>>TD;config["readout"]>>TR;
  config["acc_n"]>>ACC_N;config["acc_w"]>>ACC_W;
  config["gyr_n"]>>GYR_N;config["gyr_w"]>>GYR_W;
  // Published settings: reviewed calibration trials can hold geometry/time
  // fixed, while historical diagnostic controls retain their original defaults.
  if(!config["estimate_extrinsic"].empty())config["estimate_extrinsic"]>>ESTIMATE_EXTRINSIC;
  if(!config["estimate_td"].empty())config["estimate_td"]>>ESTIMATE_TD;
  if((ESTIMATE_EXTRINSIC!=0&&ESTIMATE_EXTRINSIC!=1)||
     (ESTIMATE_TD!=0&&ESTIMATE_TD!=1))return 7;
  // Experimental explicit opt-in. Upstream selects ProjectionFactor when td
  // is fixed, which otherwise omits its rolling-shutter row correction.
  int fixedTimeRows=0;
  if(!config["fixed_time_row_correction"].empty())config["fixed_time_row_correction"]>>fixedTimeRows;
  if((fixedTimeRows!=0&&fixedTimeRows!=1)||
     (fixedTimeRows && (ESTIMATE_TD!=0||!std::isfinite(TR)||TR<0||TR>.1)))return 7;
  long long replayStart=0;
  if(!config["replay_start_ns"].empty()){
    std::string start; config["replay_start_ns"]>>start;
    if(start.empty()||start.find_first_not_of("0123456789")!=std::string::npos)return 7;
    try { replayStart=std::stoll(start); } catch(const std::exception&) { return 7; }
  }
  EX_CALIB_RESULT_PATH=directory+"/estimated-extrinsics.txt";
  VINS_RESULT_PATH=directory+"/unused-vins-result.csv";
  std::ifstream imuf(directory+"/imu.csv"),featuref(directory+"/features.csv");
  std::string line;std::getline(imuf,line);std::vector<Imu> imu;
  while(std::getline(imuf,line)){
    auto v=split(line);if(v.size()!=7)return 4;
    if(v[0]<replayStart)continue;
    imu.push_back({v[0]/1e9,Eigen::Vector3d(v[4],v[5],v[6]),Eigen::Vector3d(v[1],v[2],v[3])});
  }
  std::map<long long,Features> frames;std::getline(featuref,line);
  while(std::getline(featuref,line)){
    auto v=split(line);if(v.size()!=8)return 5;
    if(v[0]<replayStart)continue;
    Eigen::Matrix<double,7,1> f;f<<v[2],v[3],1,v[4],v[5],v[6],v[7];
    if(fixedTimeRows)correctFixedTimeObservation(f,TR,ROW);
    frames[static_cast<long long>(v[0])][static_cast<int>(v[1])].push_back({0,f});
  }
  // Upstream ROS uses a global Estimator: static zero initialization is essential
  // before its constructor inspects the preintegration pointer array.
  if(imu.empty())return 4;
#ifdef GAIT_ANDROID_REPLAY
  // Upstream clearState does not reset every scalar (including gravity).
  // Recreate the object in zeroed aligned storage for each JNI recording, matching
  // the upstream process-start static-zero contract without leaking prior state.
  alignas(Estimator) static unsigned char storage[sizeof(Estimator)]={};
  static Estimator* previous=nullptr;
  if(previous){previous->clearState();previous->~Estimator();}
  std::memset(storage,0,sizeof(storage));
  previous=new(storage) Estimator();
  Estimator& estimator=*previous;
#else
  static Estimator estimator;
#endif
  estimator.setParameter();
#ifdef GAIT_ANDROID_REPLAY
  // A brief stationary observation learns gyro bias; geometry/time stay calibrated.
  cv::Mat initialBias; config["initialGyroBias"]>>initialBias;
  if(!initialBias.empty()){
    if(initialBias.total()!=3)return 7;
    Eigen::Vector3d bias;cv::cv2eigen(initialBias,bias);
    if(!bias.allFinite()||bias.norm()>=.08)return 7;
    for(int i=0;i<=WINDOW_SIZE;i++)estimator.Bgs[i]=bias;
  }
#endif
  std::ofstream output(directory+"/"+prefix+"-states.csv");
  output<<"camera_time_s,imu_time_s,initialized,px,py,pz,vx,vy,vz,ba_norm,bg_norm,td,features,processing_ms,reboot,tic_norm,g_norm,rotation_change_deg\n";
  output<<std::setprecision(17);
  // Integration starts at a genuine first IMU sample, never extrapolates.
  size_t index=0;double current=imu.at(0).t;
  estimator.processIMU(0,imu[0].a,imu[0].g);
  Eigen::Vector3d lastA=imu[0].a,lastG=imu[0].g;
  int emitted=0,initialized=0;
  for(const auto& frame:frames){
    double cameraTime=frame.first/1e9, target=cameraTime+estimator.td;
    if(target<=current || target>=imu.back().t)continue;
    TicToc timer;
    while(index+1<imu.size() && imu[index+1].t<=target){
      ++index;auto& s=imu[index];
      estimator.processIMU(s.t-current,s.a,s.g);current=s.t;lastA=s.a;lastG=s.g;
    }
    const auto& next=imu.at(index+1);
    double w=(target-current)/(next.t-current);
    Eigen::Vector3d a=(1-w)*lastA+w*next.a,g=(1-w)*lastG+w*next.g;
    estimator.processIMU(target-current,a,g);current=target;lastA=a;lastG=g;
    std_msgs::Header header;header.stamp.value=cameraTime;
    estimator.processImage(frame.second,header);
    bool ready=estimator.solver_flag==Estimator::NON_LINEAR;
    initialized+=ready; ++emitted;
    auto p=estimator.Ps[WINDOW_SIZE],v=estimator.Vs[WINDOW_SIZE];
    output<<cameraTime<<','<<target<<','<<ready<<','<<p.x()<<','<<p.y()<<','<<p.z()<<','
          <<v.x()<<','<<v.y()<<','<<v.z()<<','<<estimator.Bas[WINDOW_SIZE].norm()<<','
          <<estimator.Bgs[WINDOW_SIZE].norm()<<','<<estimator.td<<','<<frame.second.size()<<','
          <<timer.toc()<<','<<estimator.failure_occur<<','<<estimator.tic[0].norm()<<','
          <<estimator.g.norm()<<','<<Eigen::AngleAxisd(rotation.transpose()*estimator.ric[0]).angle()*180/M_PI<<'\n';
  }
  std::cout<<"frames="<<emitted<<" initialized_frames="<<initialized
           <<" fixed_time_row_correction="<<fixedTimeRows<<" replay_start_ns="<<replayStart<<" distanceReady=false\n";
  return emitted==0 ? 6 : 0;
}
