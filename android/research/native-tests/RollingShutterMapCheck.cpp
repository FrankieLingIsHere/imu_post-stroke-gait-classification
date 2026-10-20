// Geometric invariants on the production mapping, not recorded phone evidence.
#include <iostream>
#include <stdexcept>
#include "cam/CamRadtan.h"
#include "rolling_shutter_map.h"
#include "reference_radtan5.h"
void check(bool v){if(!v)throw std::runtime_error("Row correction invariant failed");}
int main(){
 auto camera=std::make_shared<ov_core::CamRadtan>(640,480);Eigen::VectorXd k(8);
 k<<499.8994237422053,495.47124377175476,320.0498287147801,247.3479547850306,.18779179474188504,-.677554908612503,.0013582373342518005,.0036323458398407017;camera->set_value(k);
 int nodes=0,rejected=0;
 for(int y=0;y<31;y++)for(int x=0;x<41;x++){
  Eigen::Vector2f pixel(x*639.f/40,y*479.f/30);auto mapped=gait::rowMapPoint(pixel,camera,Eigen::Vector3d::Zero(),.016);
  check(mapped.source.allFinite()&&(mapped.source-pixel).norm()==0);nodes++;rejected+=!mapped.valid;
 }
 check(rejected>0&&rejected<nodes/2);
 k<<500,500,320,240,0,0,0,0;camera->set_value(k);
 Eigen::Vector2f pixel(400,280);Eigen::Vector3d angular(.1,-.2,.3),ray((pixel.x()-320)/500,(pixel.y()-240)/500,1);
 ray=ov_core::exp_so3(-angular*.01)*ray;Eigen::Vector2f expected(500*ray.x()/ray.z()+320,500*ray.y()/ray.z()+240);
 auto mapped=gait::rowMapPoint(pixel,camera,angular,.01);check(mapped.valid&&(mapped.source-expected).norm()<.0001);
 auto backward=gait::rowMapPoint(pixel,camera,-angular,.01);check(backward.valid&&((mapped.source-pixel)+(backward.source-pixel)).norm()<.01);
 auto full=std::make_shared<gait::ReferenceRadtan5>(640,480,.8721847219970491);
 k<<499.8994237422053,495.47124377175476,320.0498287147801,247.3479547850306,.18779179474188504,-.677554908612503,.0013582373342518005,.0036323458398407017;full->set_value(k);
 for(int y=0;y<31;y++)for(int x=0;x<41;x++){
  Eigen::Vector2f pixel(x*639.f/40,y*479.f/30);auto q=gait::rowMapPoint(pixel,full,Eigen::Vector3d::Zero(),.016);
  check(q.valid&&(q.source-pixel).norm()==0);check((full->distort_f(full->undistort_f(pixel))-pixel).norm()<.001);
 }
 Eigen::Vector2d pt(.32,-.21);Eigen::MatrixXd H,J;full->compute_distort_jacobian(pt,H,J);
 for(int i=0;i<2;i++){
  Eigen::Vector2f a=pt.cast<float>(),b=a;a(i)+=.001;b(i)-=.001;
  check((((full->distort_f(a)-full->distort_f(b))/.002).cast<double>()-H.col(i)).norm()<.05);
 }
 std::cout<<"PASS: "<<nodes<<" zero-rotation identity nodes, invalid lens-ray rejection, analytic rotation, full radtan5 inversion and Jacobian checks.\n";
}
