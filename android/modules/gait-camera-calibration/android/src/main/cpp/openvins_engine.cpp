// GPL-3.0-or-later. Android transport for the pinned OpenVINS estimator.
// Factory/optical seeds are priors, never measured walking distance.
#include <mutex>
#include <deque>
#include <memory>
#include <sstream>
#include <fstream>
#include <iomanip>
#include <chrono>
#include <cmath>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include "core/VioManager.h"
#include "state/StateHelper.h"
#include "state/State.h"
#include "utils/quat_ops.h"
#include "rolling_shutter_map.h"
#include "reference_radtan5.h"
#ifndef GAIT_OPENVINS_HOST
#include <jni.h>
#endif

namespace gait {
using namespace ov_core;
using namespace ov_msckf;
static std::mutex lock;
static std::unique_ptr<class Engine> engine;
static long serial=0;
static void check(bool yes,const char* reason){if(!yes)throw std::runtime_error(reason);}

class Engine {
 public:
  std::shared_ptr<VioManager> vio;
  bool calibrating;
  double origin=-1,lastImu=-1,lastFrame=-1,firstTracked=-1,readout=0;
  int updates=0;
  Eigen::Vector3d angle=Eigen::Vector3d::Zero();
  std::deque<ImuData> recent;
  Eigen::VectorXd seed;
  Eigen::Matrix3d seedRotation;
  bool integrity=true;
  cv::Mat rowMask;
  bool fullReferenceLens=false;
  double fixedLensK3=0;
#ifdef GAIT_OPENVINS_HOST
  // Offline ablations only. Android builds cannot override measured correction.
  double diagnosticRowRotationSign=1;
#endif
  void beginMotion(){vio->gait_begin_motion();}
  void endMotion(){vio->gait_end_motion();}
  explicit Engine(const std::string& config){
    cv::FileStorage file(config,cv::FileStorage::READ);
    check(file.isOpened(),"Phone tracking configuration is missing");
    cv::Mat k,e;file["intrinsics"]>>k;file["extrinsics"]>>e;
    int mode=0;file["calibrating"]>>mode;calibrating=mode==1;
    check(k.total()==8&&e.total()==7,"Invalid phone tracking geometry");
    VioManagerOptions p;p.use_aruco=false;
    p.state_options.do_calib_camera_pose=calibrating;
    p.state_options.do_calib_camera_intrinsics=calibrating;
    p.state_options.do_calib_camera_timeoffset=calibrating;
#ifdef GAIT_OPENVINS_HOST
    // Parameter-group ablations for the notebook only. Never change an EKF's
    // state allocation mid-run, or expose these overrides to the Android app.
    std::string group="joint";
    if(!file["diagnostic_calibration_group"].empty())file["diagnostic_calibration_group"]>>group;
    check(group=="joint"||group=="optics"||group=="alignment","Invalid calibration ablation");
    if(group=="optics")p.state_options.do_calib_camera_pose=p.state_options.do_calib_camera_timeoffset=false;
    if(group=="alignment")p.state_options.do_calib_camera_intrinsics=false;
#endif
    p.state_options.max_clone_size=11;p.state_options.max_slam_features=15;
    p.state_options.max_msckf_in_update=75;p.state_options.max_slam_in_update=15;
    p.num_pts=150;p.init_options.init_max_features=100;
    p.init_options.init_window_time=2;p.init_options.init_imu_thresh=.3;
    // First setup must establish the instructed quiet baseline, not silently
    // initialize from movement after a timed cue. Bound walking profiles retain
    // dynamic recovery; unknown geometry starts with static initialization only.
    p.init_options.init_max_disparity=2;p.init_options.init_dyn_use=!calibrating;
    // The pinned initializer does not export its optimized calibration states
    // or their cross-covariance (DynamicInitializer.cpp has an explicit TODO).
    // Keep initialization geometry consistent with the tracker. Calibration
    // remains enabled in the running EKF; never discard optimized geometry.
    p.init_options.init_dyn_mle_opt_calib=false;
    p.init_options.init_dyn_mle_max_threads=2;
    p.init_options.init_dyn_mle_max_time=.25;
#ifdef GAIT_OPENVINS_HOST
    if(!file["diagnostic_row_rotation_sign"].empty())file["diagnostic_row_rotation_sign"]>>diagnosticRowRotationSign;
    if(!file["diagnostic_init_seconds"].empty())file["diagnostic_init_seconds"]>>p.init_options.init_dyn_mle_max_time;
    if(!file["diagnostic_init_iterations"].empty())file["diagnostic_init_iterations"]>>p.init_options.init_dyn_mle_max_iter;
    if(!file["diagnostic_init_disparity"].empty())file["diagnostic_init_disparity"]>>p.init_options.init_max_disparity;
    if(!file["diagnostic_init_min_degrees"].empty())file["diagnostic_init_min_degrees"]>>p.init_options.init_dyn_min_deg;
    if(!file["diagnostic_init_window_seconds"].empty())file["diagnostic_init_window_seconds"]>>p.init_options.init_window_time;
    check(diagnosticRowRotationSign==-1||diagnosticRowRotationSign==0||diagnosticRowRotationSign==1,"Invalid host row ablation");
#endif
    p.try_zupt=true;p.zupt_max_velocity=.15;p.zupt_max_disparity=.5;
    p.zupt_noise_multiplier=10;p.zupt_only_at_beginning=false;
    // Programmatic construction bypasses the upstream estimator YAML. Its
    // header fallback is 5, but the pinned Euroc/simulation/RealSense configs
    // use 1 for visual innovation rejection. Match that intended 95% chi-square
    // threshold instead of admitting residuals up to five times the bound.
    // This does not change uncertainty/readiness limits or disable FEJ.
    p.msckf_options.chi2_multipler=p.slam_options.chi2_multipler=1;
#ifdef GAIT_OPENVINS_HOST
    // Notebook-only consistency ablation. Pixel uncertainty and rejection are
    // kept distinct; both MSCKF and persistent SLAM measurements use the same
    // specified model. Never loosen a production admission gate from this test.
    double pixelSigma=1,chiMultiplier=5;
    if(!file["diagnostic_pixel_sigma"].empty())file["diagnostic_pixel_sigma"]>>pixelSigma;
    if(!file["diagnostic_chi_multiplier"].empty())file["diagnostic_chi_multiplier"]>>chiMultiplier;
    check(std::isfinite(pixelSigma)&&pixelSigma>=.25&&pixelSigma<=5&&std::isfinite(chiMultiplier)&&chiMultiplier>=1&&chiMultiplier<=5,"Invalid visual consistency ablation");
    p.msckf_options.sigma_pix=p.slam_options.sigma_pix=pixelSigma;
    p.msckf_options.sigma_pix_sq=p.slam_options.sigma_pix_sq=pixelSigma*pixelSigma;
    p.msckf_options.chi2_multipler=p.slam_options.chi2_multipler=chiMultiplier;
#endif
    p.use_multi_threading_subs=false;p.use_multi_threading_pubs=false;
    p.num_opencv_threads=2;p.use_stereo=false;p.track_frequency=20;
    p.gravity_mag=9.80665;
    p.init_options.gravity_mag=p.gravity_mag;
    p.vec_dw<<1,0,0,1,0,1;p.vec_da=p.vec_dw;p.vec_tg.setZero();
    p.q_ACCtoIMU<<0,0,0,1;p.q_GYROtoIMU=p.q_ACCtoIMU;
    file["td"]>>p.calib_camimu_dt;
    file["acc_noise_density"]>>p.imu_noises.sigma_a;
    file["gyro_noise_density"]>>p.imu_noises.sigma_w;
    // Continuous-time units; do not reuse per-sample standard deviation as density.
    p.imu_noises.sigma_ab=.0002;p.imu_noises.sigma_wb=.00002;
    // Programmatic construction bypasses upstream YAML loading. The initializer
    // owns a separate noise options object; leaving its defaults would solve
    // and weight the same readings differently from the running estimator.
    p.init_options.sigma_a=p.imu_noises.sigma_a;
    p.init_options.sigma_w=p.imu_noises.sigma_w;
    p.init_options.sigma_ab=p.imu_noises.sigma_ab;
    p.init_options.sigma_wb=p.imu_noises.sigma_wb;
    seed.resize(8);Eigen::VectorXd pose(7);
    for(int i=0;i<8;i++)seed(i)=k.at<double>(i);
    for(int i=0;i<7;i++)pose(i)=e.at<double>(i);
    check(seed.allFinite()&&pose.allFinite()&&seed(0)>=150&&seed(1)>=150&&seed(0)<=1600&&seed(1)<=1600,"Invalid camera seed");
    check(std::abs(pose.head<4>().norm()-1)<1e-5&&pose.tail<3>().norm()<=.25,"Invalid alignment seed");
    if(!file["reference_lens_k3"].empty()){
      double k3;file["reference_lens_k3"]>>k3;
      check(!calibrating&&std::isfinite(k3)&&std::abs(k3)<=1,"Invalid fixed reference lens coefficient");
      fullReferenceLens=true;fixedLensK3=k3;
      p.camera_intrinsics[0]=std::make_shared<ReferenceRadtan5>(640,480,k3);
    }else p.camera_intrinsics[0]=std::make_shared<ReferenceRadtan5>(640,480,0);
    p.camera_intrinsics[0]->set_value(seed);p.camera_extrinsics[0]=pose;
    p.init_options.camera_intrinsics=p.camera_intrinsics;
    p.init_options.camera_extrinsics=p.camera_extrinsics;
    p.init_options.calib_camimu_dt=p.calib_camimu_dt;p.init_options.use_stereo=false;
#ifdef GAIT_OPENVINS_DIAGNOSTICS
    Printer::setPrintLevel(Printer::PrintLevel::DEBUG);
#else
    Printer::setPrintLevel(Printer::PrintLevel::SILENT);
#endif
    vio=std::make_shared<VioManager>(p);
    auto s=vio->get_state();seedRotation=s->_calib_IMUtoCAM.at(0)->Rot();
    if(calibrating){
      Eigen::MatrixXd cov=Eigen::MatrixXd::Zero(15,15);
      Eigen::VectorXd sd(15);sd<<seed(0)*.1,seed(1)*.1,10,10,.05,.05,.01,.01,.05,.05,.05,.05,.05,.05,.01;
      cov.diagonal()=sd.array().square().matrix();
      std::vector<std::shared_ptr<ov_type::Type>> variables;
      std::vector<int> indices;
      if(p.state_options.do_calib_camera_intrinsics){variables.push_back(s->_cam_intrinsics.at(0));for(int i=0;i<8;i++)indices.push_back(i);}
      if(p.state_options.do_calib_camera_pose){variables.push_back(s->_calib_IMUtoCAM.at(0));for(int i=8;i<14;i++)indices.push_back(i);}
      if(p.state_options.do_calib_camera_timeoffset){variables.push_back(s->_calib_dt_CAMtoIMU);indices.push_back(14);}
      Eigen::MatrixXd active=Eigen::MatrixXd::Zero(indices.size(),indices.size());
      for(size_t i=0;i<indices.size();i++)active(i,i)=cov(indices[i],indices[i]);
      StateHelper::set_initial_covariance(s,active,variables);
    }
  }
  void imu(long long ns,const Eigen::Vector3d& a,const Eigen::Vector3d& g){
    const double t=ns/1e9;
    check(a.allFinite()&&g.allFinite()&&a.norm()<150&&g.norm()<20,"Invalid live IMU reading");
    check(t>lastImu,"IMU timestamp did not advance");
    if(lastImu>0){const double dt=t-lastImu;if(dt>.05)integrity=false;angle+=g.cwiseAbs()*dt;}
    if(origin<0)origin=t;
    ImuData m;m.timestamp=t;m.am=a;m.wm=g;vio->feed_measurement_imu(m);
    recent.push_back(m);while(!recent.empty()&&t-recent.front().timestamp>2)recent.pop_front();lastImu=t;
  }
  cv::Mat compensate(const cv::Mat& image,double t,double skew){
    rowMask=cv::Mat::zeros(image.size(),CV_8U);
    if(skew==0)return image;
    check(skew>0&&skew<=.1,"Invalid rolling shutter timing");
    const double dt=vio->get_state()->_calib_dt_CAMtoIMU->value()(0);
    check(!recent.empty()&&recent.front().timestamp<=t+dt-skew/2&&recent.back().timestamp>=t+dt+skew/2,"Missing rolling shutter IMU coverage");
    Eigen::Vector3d mean=Eigen::Vector3d::Zero();int n=0;
    for(const auto& r:recent)if(std::abs(r.timestamp-t-dt)<=skew/2+.005){mean+=r.wm;++n;}
    check(n>=2,"Sparse rolling shutter IMU coverage");mean/=n;
    auto state=vio->get_state();mean-=state->_imu->bias_g();
    auto camera=state->_cam_intrinsics_cameras.at(0);
    Eigen::Vector3d angular=state->_calib_IMUtoCAM.at(0)->Rot()*mean;
#ifdef GAIT_OPENVINS_HOST
    if(diagnosticRowRotationSign==0)return image;
    angular*=diagnosticRowRotationSign;
#endif
    // Rotational row correction at the measured middle-exposure timestamp.
    // Translation/readout coupling remains a physical validation requirement.
    cv::Mat mx(31,41,CV_32F),my(31,41,CV_32F),valid(31,41,CV_8U);
    for(int y=0;y<31;y++)for(int x=0;x<41;x++){
      Eigen::Vector2f pixel(x*639.f/40,y*479.f/30);
      const double rowtime=(pixel.y()/479-.5)*skew;
      const auto q=rowMapPoint(pixel,camera,angular,rowtime);
      mx.at<float>(y,x)=q.source.x();my.at<float>(y,x)=q.source.y();valid.at<unsigned char>(y,x)=q.valid?1:0;
    }
    cv::Mat fullx(480,640,CV_32F),fully(480,640,CV_32F),out;
    // Align grid corners explicitly: resize() uses pixel centres and shifts even
    // the identity map by several pixels at this grid resolution.
    for(int y=0;y<480;y++)for(int x=0;x<640;x++){
      float a=x*40.f/639,b=y*30.f/479;int i=std::min(39,(int)a),j=std::min(29,(int)b);a-=i;b-=j;
      auto interp=[&](const cv::Mat& map){return (1-b)*((1-a)*map.at<float>(j,i)+a*map.at<float>(j,i+1))+b*((1-a)*map.at<float>(j+1,i)+a*map.at<float>(j+1,i+1));};
      fullx.at<float>(y,x)=interp(mx);fully.at<float>(y,x)=interp(my);
      if(!valid.at<unsigned char>(j,i)||!valid.at<unsigned char>(j,i+1)||!valid.at<unsigned char>(j+1,i)||!valid.at<unsigned char>(j+1,i+1))rowMask.at<unsigned char>(y,x)=255;
    }
    cv::remap(image,out,fullx,fully,cv::INTER_LINEAR,cv::BORDER_CONSTANT);return out;
  }
  std::string frame(long long ns,const cv::Mat& image,double skew){
    double t=ns/1e9;
    check(image.cols==640&&image.rows==480&&image.type()==CV_8UC1,"Invalid live camera frame");
    check(t>lastFrame&&lastImu>t+.005,"Camera must wait for its actual IMU coverage");
    if(lastFrame>0&&t-lastFrame>.2)integrity=false;
    readout=skew;
    auto corrected=compensate(image,t,skew);
    CameraData m;m.timestamp=t;m.sensor_ids={0};m.images={corrected};m.masks={rowMask};
    vio->feed_measurement_camera(m);lastFrame=t;
    // Upstream initialized() also waits for the first moving visual update.
    // Static initialization plus a current accepted zero-motion update must be
    // visible before Go, otherwise a still user can never start the walk.
    auto s=vio->get_state();bool initialized=vio->initialized_time()>=origin&&std::abs(s->_timestamp-t)<.001;
    auto f=vio->get_good_features_MSCKF();
    if(initialized){updates++;if(firstTracked<0)firstTracked=t;}
    const Eigen::VectorXd k=s->_cam_intrinsics.at(0)->value(),pose=s->_calib_IMUtoCAM.at(0)->value();
    Eigen::VectorXd stds=Eigen::VectorXd::Constant(15,1e6);
    if(calibrating){
      stds.setZero();
      auto extract=[&](std::shared_ptr<ov_type::Type> variable,int offset,int size){
        if(variable->id()<0)return;
        auto c=StateHelper::get_marginal_covariance(s,{variable});
        check(c.allFinite()&&(c.diagonal().array()>=0).all(),"Invalid calibration covariance");
        stds.segment(offset,size)=c.diagonal().array().sqrt();
      };
      extract(s->_cam_intrinsics.at(0),0,8);extract(s->_calib_IMUtoCAM.at(0),8,6);extract(s->_calib_dt_CAMtoIMU,14,1);
    }
    bool ready=initialized&&integrity&&updates>=200&&t-firstTracked>=15&&angle.minCoeff()>=.5&&
      stds(0)/k(0)<.04&&stds(1)/k(1)<.04&&stds.segment<2>(2).maxCoeff()<6&&
      stds.segment<3>(8).maxCoeff()<.035&&stds.segment<3>(11).maxCoeff()<.015&&stds(14)<.003;
    auto p=s->_imu->pos(),v=s->_imu->vel();
    auto pcov=StateHelper::get_marginal_covariance(s,{s->_imu});
    double positionStd=pcov.block<3,3>(3,3).diagonal().maxCoeff();check(pcov.allFinite()&&(pcov.diagonal().array()>=0).all(),"Invalid tracking covariance");positionStd=std::sqrt(positionStd);
    ready=ready&&positionStd<.15&&v.norm()<3&&s->_imu->bias_a().norm()<1&&s->_imu->bias_g().norm()<.2&&pose.tail<3>().norm()<=.25;
    std::ostringstream o;o<<std::setprecision(17)<<"{\"initialized\":"<<(initialized?"true":"false")<<",\"integrity\":"<<(integrity?"true":"false")
      <<",\"numericalCalibrationReady\":"<<(ready?"true":"false")<<",\"timestampSeconds\":"<<t<<",\"updates\":"<<updates
      <<",\"positionStdMetres\":"<<positionStd<<",\"features\":"<<f.size()<<",\"readoutSeconds\":"<<skew<<",\"cameraValues\":[";
    for(int i=0;i<8;i++)o<<(i?",":"")<<k(i);o<<"],\"imuToCamera\":[";
    for(int i=0;i<7;i++)o<<(i?",":"")<<pose(i);o<<"],\"calibrationStd\":[";
    for(int i=0;i<15;i++)o<<(i?",":"")<<stds(i);o<<"],\"axisMotionRadians\":["<<angle.x()<<','<<angle.y()<<','<<angle.z()<<"]";
    o<<",\"fixedLensK3\":";
    if(fullReferenceLens)o<<fixedLensK3;else o<<"null";
    o<<",\"timeOffsetSeconds\":"<<s->_calib_dt_CAMtoIMU->value()(0)<<",\"state\":{\"imu_time_s\":"<<t+s->_calib_dt_CAMtoIMU->value()(0)
      <<",\"camera_time_s\":"<<t<<",\"initialized\":"<<(initialized?1:0)<<",\"px\":"<<p.x()<<",\"py\":"<<p.y()<<",\"pz\":"<<p.z()
      <<",\"vx\":"<<v.x()<<",\"vy\":"<<v.y()<<",\"vz\":"<<v.z()<<",\"ba_norm\":"<<s->_imu->bias_a().norm()<<",\"bg_norm\":"<<s->_imu->bias_g().norm()
      <<",\"tic_norm\":"<<pose.tail<3>().norm()<<",\"g_norm\":9.80665,\"rotation_change_deg\":"<<Eigen::AngleAxisd(seedRotation.transpose()*s->_calib_IMUtoCAM.at(0)->Rot()).angle()*180/M_PI
      <<",\"reboot\":"<<(integrity?0:1)<<",\"position_std_m\":"<<positionStd<<"}}";
    auto str=o.str();check(str.find("nan")==std::string::npos&&str.find("inf")==std::string::npos,"Estimator returned nonfinite state");return str;
  }
};
}

#ifdef GAIT_OPENVINS_HOST
#ifndef GAIT_OPENVINS_NO_MAIN
// Host executable runs the same transport/estimator; no simulated Android claim.
int main(int argc,char** argv){if(argc!=4&&argc!=5&&argc!=6)return 2;try{
 gait::Engine e(argv[1]);std::ifstream imu(argv[2]),frames(argv[3]);std::string line;std::getline(imu,line);std::getline(frames,line);
 struct Row{long long ns;Eigen::Vector3d a,g;};std::vector<Row> rows;
 while(std::getline(imu,line)){std::replace(line.begin(),line.end(),',',' ');std::istringstream s(line);Row r;s>>r.ns>>r.g.x()>>r.g.y()>>r.g.z()>>r.a.x()>>r.a.y()>>r.a.z();rows.push_back(r);}
 size_t i=0;bool moving=false,ended=false;long long motionNs=argc>=5?std::stoll(argv[4]):-1,endNs=argc==6?std::stoll(argv[5]):-1;
 while(std::getline(frames,line)){
   auto c=line.find(',');long long ns=std::stoll(line.substr(0,c));auto path=line.substr(c+1);
   if(!path.empty()&&path.back()=='\r')path.pop_back();
   double skew=0;auto separator=path.rfind(',');
   if(separator!=std::string::npos){skew=std::stod(path.substr(separator+1));path=path.substr(0,separator);}
   if(motionNs<0)motionNs=ns+3000000000LL;
   while(i<rows.size()&&rows[i].ns<ns+200000000L){e.imu(rows[i].ns,rows[i].a,rows[i].g);i++;}
   if(i==rows.size())break;
   if(!moving&&ns>=motionNs){e.beginMotion();moving=true;}
   if(endNs>0&&!ended&&ns>=endNs){e.endMotion();ended=true;}
   auto start=std::chrono::steady_clock::now();auto result=e.frame(ns,cv::imread(path,0),skew);
   double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
   result.pop_back();std::cout<<result<<",\"processingSeconds\":"<<seconds<<"}"<<'\n';
 }return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 9;}}
#endif
#else
static void error(JNIEnv* e,const std::exception& x){e->ThrowNew(e->FindClass("java/lang/IllegalStateException"),x.what());}
extern "C" JNIEXPORT jlong JNICALL Java_expo_modules_gaitcalibration_OnDeviceVio_nativeStart(JNIEnv* env,jclass,jstring config){
 std::lock_guard<std::mutex> guard(gait::lock);try{gait::check(!gait::engine,"Tracking is already running");const char* v=env->GetStringUTFChars(config,0);std::string path(v);env->ReleaseStringUTFChars(config,v);gait::engine.reset(new gait::Engine(path));return ++gait::serial;}catch(const std::exception& e){error(env,e);return 0;}}
extern "C" JNIEXPORT void JNICALL Java_expo_modules_gaitcalibration_OnDeviceVio_nativeImu(JNIEnv* env,jclass,jlong handle,jlong ns,jdouble ax,jdouble ay,jdouble az,jdouble gx,jdouble gy,jdouble gz){
 std::lock_guard<std::mutex> guard(gait::lock);try{gait::check(handle==gait::serial&&gait::engine,"Tracking session ended");gait::engine->imu(ns,{ax,ay,az},{gx,gy,gz});}catch(const std::exception& e){error(env,e);}}
extern "C" JNIEXPORT jstring JNICALL Java_expo_modules_gaitcalibration_OnDeviceVio_nativeFrame(JNIEnv* env,jclass,jlong handle,jlong ns,jstring filename,jdouble skew){
 std::lock_guard<std::mutex> guard(gait::lock);try{gait::check(handle==gait::serial&&gait::engine,"Tracking session ended");const char* v=env->GetStringUTFChars(filename,0);std::string path(v);env->ReleaseStringUTFChars(filename,v);auto result=gait::engine->frame(ns,cv::imread(path,0),skew);return env->NewStringUTF(result.c_str());}catch(const std::exception& e){error(env,e);return 0;}}
extern "C" JNIEXPORT void JNICALL Java_expo_modules_gaitcalibration_OnDeviceVio_nativeStop(JNIEnv*,jclass,jlong handle){std::lock_guard<std::mutex> guard(gait::lock);if(handle==gait::serial)gait::engine.reset();}
extern "C" JNIEXPORT void JNICALL Java_expo_modules_gaitcalibration_OnDeviceVio_nativeBeginMotion(JNIEnv* env,jclass,jlong handle){
 std::lock_guard<std::mutex> guard(gait::lock);try{gait::check(handle==gait::serial&&gait::engine,"Tracking session ended");gait::engine->beginMotion();}catch(const std::exception& e){error(env,e);}}
extern "C" JNIEXPORT void JNICALL Java_expo_modules_gaitcalibration_OnDeviceVio_nativeEndMotion(JNIEnv* env,jclass,jlong handle){
 std::lock_guard<std::mutex> guard(gait::lock);try{gait::check(handle==gait::serial&&gait::engine,"Tracking session ended");gait::engine->endMotion();}catch(const std::exception& e){error(env,e);}}
#endif
