// GPL-3.0-or-later. Diagnostic projection only; NOT an admitted tracking model.
// Upstream dynamic initialization has a separate radtan4 factor. Passing these
// projection tests does not establish a consistent full estimator.
#pragma once
#include "cam/CamRadtan.h"
namespace gait {
// OpenVINS retains its eight-state parameter layout. k3 is a fixed reference
// coefficient, never a learned ninth parameter or an inferred factory value.
class ReferenceRadtan5 : public ov_core::CamRadtan {
  double k3;
 public:
  ReferenceRadtan5(int w,int h,double value):CamRadtan(w,h),k3(value){}
  Eigen::Vector2f undistort_f(const Eigen::Vector2f& pixel) override {
    cv::Mat src(1,1,CV_64FC2),dst;src.at<cv::Vec2d>(0,0)={pixel.x(),pixel.y()};
    auto k=get_value();cv::Matx33d K(k(0),0,k(2),0,k(1),k(3),0,0,1);
    cv::Vec<double,5> d(k(4),k(5),k(6),k(7),k3);
    cv::undistortPoints(src,dst,K,d,cv::noArray(),cv::noArray(),cv::TermCriteria(cv::TermCriteria::COUNT|cv::TermCriteria::EPS,100,1e-10));
    auto p=dst.at<cv::Vec2d>(0,0);return {float(p[0]),float(p[1])};
  }
  Eigen::Vector2f distort_f(const Eigen::Vector2f& p) override {
    auto k=get_value();double r2=p.squaredNorm(),r6=r2*r2*r2;
    auto out=CamRadtan::distort_f(p);out.x()+=float(k(0)*p.x()*k3*r6);out.y()+=float(k(1)*p.y()*k3*r6);return out;
  }
  void compute_distort_jacobian(const Eigen::Vector2d& p,Eigen::MatrixXd& H,Eigen::MatrixXd& J) override {
    CamRadtan::compute_distort_jacobian(p,H,J);
    auto k=get_value();double x=p.x(),y=p.y(),r2=p.squaredNorm(),r4=r2*r2,r6=r4*r2;
    H(0,0)+=k(0)*k3*(r6+6*x*x*r4);H(0,1)+=k(0)*k3*6*x*y*r4;
    H(1,0)+=k(1)*k3*6*x*y*r4;H(1,1)+=k(1)*k3*(r6+6*y*y*r4);
    J(0,0)+=x*k3*r6;J(1,1)+=y*k3*r6;
  }
};
}
