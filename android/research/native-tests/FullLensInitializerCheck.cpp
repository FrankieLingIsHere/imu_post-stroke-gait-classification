// Test the actual patched Ceres factor against OpenCV and finite differences.
#include <iostream>
#include <stdexcept>
#include "ceres/Factor_ImageReprojCalib.h"
#include "reference_radtan5.h"
void check(bool ok){if(!ok)throw std::runtime_error("Initializer lens contract mismatch");}
int main(){
 double k3=.8721847219970491;
 double q[]={0,0,0,1},p[]={0,0,0},f[]={.64,-.42,2},e[]={0,0,0,1},t[]={0,0,0};
 double k[]={499.8994237422053,495.47124377175476,320.0498287147801,247.3479547850306,.18779179474188504,-.677554908612503,.0013582373342518005,.0036323458398407017};
 cv::Matx33d K(k[0],0,k[2],0,k[1],k[3],0,0,1);cv::Vec<double,5> d(k[4],k[5],k[6],k[7],k3);
 std::vector<cv::Point3d> object={{f[0],f[1],f[2]}};std::vector<cv::Point2d> pixels;
 cv::projectPoints(object,cv::Vec3d(0,0,0),cv::Vec3d(0,0,0),K,d,pixels);
 ov_init::Factor_ImageReprojCalib factor({pixels[0].x,pixels[0].y},1,false,k3);
 const double* params[]={q,p,f,e,t,k};double r[2],jf[6],jk[16];double* jac[]={nullptr,nullptr,jf,nullptr,nullptr,jk};
 check(factor.Evaluate(params,r,jac)&&std::hypot(r[0],r[1])<.001);
 for(int i=0;i<3;i++){
  double before=f[i],a[2],b[2];f[i]=before+.001;factor.Evaluate(params,a,nullptr);f[i]=before-.001;factor.Evaluate(params,b,nullptr);f[i]=before;
  for(int row=0;row<2;row++)check(std::abs((a[row]-b[row])/.002-jf[row*3+i])<.05);
 }
 for(int i=0;i<8;i++){
  double before=k[i],a[2],b[2],eps=i<4?.1:.001;k[i]=before+eps;factor.Evaluate(params,a,nullptr);k[i]=before-eps;factor.Evaluate(params,b,nullptr);k[i]=before;
  for(int row=0;row<2;row++)check(std::abs((a[row]-b[row])/(2*eps)-jk[row*8+i])<.05);
 }
 gait::ReferenceRadtan5 camera(640,480,k3);camera.set_value(Eigen::Map<Eigen::VectorXd>(k,8));check(camera.fixed_radial_k3()==k3);
 ov_init::Factor_ImageReprojCalib old({pixels[0].x,pixels[0].y},1,false);old.Evaluate(params,r,nullptr);
 check(std::hypot(r[0],r[1])>.1); // Control: omitting k3 really changes the residual.
 std::cout<<"PASS: full-lens initializer projection, feature/intrinsic Jacobians and omitted-k3 rejection control.\n";
}
