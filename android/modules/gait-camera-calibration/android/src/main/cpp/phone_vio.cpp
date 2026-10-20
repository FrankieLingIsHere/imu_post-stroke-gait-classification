// GPL-3.0: Android transport around pinned VINS-Mono; see THIRD_PARTY.md.
// Camera/IMU values and calibration are measured inputs. No step-length model.
#ifndef GAIT_HOST_CHECK
#include <jni.h>
#endif
#include <mutex>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/video/tracking.hpp>
#define GAIT_ANDROID_REPLAY
#define main gait_reference_main
#include "replay.cpp"
#undef main

static std::mutex runnerMutex;
static void features(const std::string& dir) {
  cv::setNumThreads(2); cv::setRNGSeed(0);
  cv::FileStorage config(dir+"/reference.yaml",cv::FileStorage::READ);
  cv::Mat K,D; config["cameraMatrix"]>>K; config["distortion"]>>D;
  if(K.rows!=3||K.cols!=3||D.total()!=5)throw std::runtime_error("Invalid lens inputs");
  std::ifstream frames(dir+"/frames.csv"); std::string line; std::getline(frames,line);
  std::ofstream out(dir+"/features.csv"); out<<std::setprecision(17)<<"timestamp_ns,id,nx,ny,u,v,vx,vy\n";
  cv::Mat previous; std::vector<cv::Point2f> points; std::vector<int> ids;
  std::map<int,cv::Point2f> oldNormals; long long previousTime=0; int nextId=0;
  while(std::getline(frames,line)) {
    auto comma=line.find(','); if(comma==std::string::npos)throw std::runtime_error("Invalid frame row");
    long long stamp=std::stoll(line.substr(0,comma)); auto filename=line.substr(comma+1);
    if(!filename.empty()&&filename.back()=='\r')filename.pop_back();
    if(stamp<=previousTime||filename.find("..")!=std::string::npos||filename.find("frames/")!=0)throw std::runtime_error("Invalid frame clock or path");
    cv::Mat current=cv::imread(dir+"/../"+filename,cv::IMREAD_GRAYSCALE);
    if(current.cols!=640||current.rows!=480)throw std::runtime_error("Invalid camera dimensions");
    if(!previous.empty()&&!points.empty()) {
      std::vector<cv::Point2f> tracked,back,old,kept;std::vector<uchar> good,reverse;std::vector<float> error;std::vector<int> keepIds;
      cv::calcOpticalFlowPyrLK(previous,current,points,tracked,good,error);
      cv::calcOpticalFlowPyrLK(current,previous,tracked,back,reverse,error);
      for(size_t i=0;i<points.size();++i)if(good[i]&&reverse[i]&&cv::norm(back[i]-points[i])<1&&tracked[i].x>1&&tracked[i].x<638&&tracked[i].y>1&&tracked[i].y<478){old.push_back(points[i]);kept.push_back(tracked[i]);keepIds.push_back(ids[i]);}
      points=kept;ids=keepIds;
      if(points.size()>=8){
        std::vector<cv::Point2f> a,b;cv::undistortPoints(old,a,K,D);cv::undistortPoints(points,b,K,D);cv::Mat mask;
        cv::findFundamentalMat(a,b,cv::FM_RANSAC,1/K.at<double>(0,0),.99,mask);
        if(!mask.empty()){kept.clear();keepIds.clear();for(size_t i=0;i<points.size();++i)if(mask.at<uchar>(i)){kept.push_back(points[i]);keepIds.push_back(ids[i]);}points=kept;ids=keepIds;}
      }
    }
    cv::Mat mask(current.size(),CV_8UC1,cv::Scalar(255));
    for(auto p:points)cv::circle(mask,cv::Point(cvRound(p.x),cvRound(p.y)),20,cv::Scalar(0),-1);
    if(points.size()<150){std::vector<cv::Point2f> extra;cv::goodFeaturesToTrack(current,extra,150-points.size(),.01,20,mask);for(auto p:extra){points.push_back(p);ids.push_back(nextId++);}}
    std::vector<cv::Point2f> normal;if(!points.empty())cv::undistortPoints(points,normal,K,D);
    std::map<int,cv::Point2f> newNormals;
    for(size_t i=0;i<points.size();++i){cv::Point2d speed(0,0);auto old=oldNormals.find(ids[i]);if(old!=oldNormals.end())speed=cv::Point2d(normal[i]-old->second)/((stamp-previousTime)/1e9);
      out<<stamp<<','<<ids[i]<<','<<normal[i].x<<','<<normal[i].y<<','<<points[i].x<<','<<points[i].y<<','<<speed.x<<','<<speed.y<<'\n';newNormals[ids[i]]=normal[i];}
    oldNormals=std::move(newNormals);previous=current;previousTime=stamp;
  }
  if(!out)throw std::runtime_error("Could not save feature tracks");
}
static int process(const std::string& dir) {
    features(dir);
    RIC.clear();TIC.clear();ESTIMATE_EXTRINSIC=0;ESTIMATE_TD=0;
    // Offline on-phone processing: fixed iteration budget, no slower-device truncation.
    SOLVER_TIME=3600;NUM_ITERATIONS=8;
    char name[]="phone-vio";std::vector<char> writable(dir.begin(),dir.end());writable.push_back(0);char* argv[]={name,writable.data()};
    return gait_reference_main(2,argv);
}
#ifdef GAIT_HOST_CHECK
int main(int argc,char** argv){if(argc<2||argc>3)return 2;try{int code=process(argv[1]);if(argc==3&&code==0){std::ifstream in(std::string(argv[1])+"/reference-states.csv");std::ofstream out(std::string(argv[1])+"/first-states.csv");out<<in.rdbuf();out.close();return process(argv[1]);}return code;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 9;}}
#else
extern "C" JNIEXPORT jint JNICALL Java_expo_modules_gaitcalibration_PhoneVio_nativeProcess(JNIEnv* env,jclass,jstring path) {
  std::lock_guard<std::mutex> lock(runnerMutex);
  const char* value=env->GetStringUTFChars(path,nullptr);std::string dir(value);env->ReleaseStringUTFChars(path,value);
  try{return process(dir);}catch(const std::exception& error){env->ThrowNew(env->FindClass("java/lang/IllegalStateException"),error.what());return -1;}
}
#endif
