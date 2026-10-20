#include "fixed_time_observation.h"
#include "factor/projection_factor.h"
#include "factor/projection_td_factor.h"
#include <cmath>
#include <iostream>

double ROW=480, TR=.03048;

int main() {
    ProjectionFactor::sqrt_info.setIdentity();
    ProjectionTdFactor::sqrt_info.setIdentity();
    double pi[7]={0,0,0,0,0,0,1}, pj[7]={.12,.03,0,0,0,0,1};
    double extrinsic[7]={.025,-.02,.003,0,0,0,1};
    double invDepth=.2, td=-.00258714;
    double* params[5]={pi,pj,extrinsic,&invDepth,&td};
    int detectsMissing=0;
    double maxResidual=0, maxDifference=0;
    for(int i=0;i<250;++i) {
        Eigen::Vector3d a(.1+.001*i,-.2+.0003*i,1);
        Eigen::Vector3d b=a-Eigen::Vector3d(.12,.03,0)*invDepth;
        Eigen::Vector2d va(.2+.001*i,-.12), vb(-.11,.18+.0005*i);
        const double ra=(i*31)%480, rb=(i*73+79)%480;
        Eigen::Vector3d rawa=a, rawb=b;
        rawa.head<2>() += TR*(ra/ROW-.5)*va;
        rawb.head<2>() += TR*(rb/ROW-.5)*vb;
        Eigen::Matrix<double,7,1> fa,fb;
        fa<<rawa.x(),rawa.y(),1,320,ra,va.x(),va.y();
        fb<<rawb.x(),rawb.y(),1,300,rb,vb.x(),vb.y();
        double oldResidual[2], referenceResidual[2], correctedResidual[2];
        ProjectionFactor old(rawa,rawb);
        old.Evaluate(params,oldResidual,nullptr);
        if(Eigen::Map<Eigen::Vector2d>(oldResidual).norm()>1e-5)++detectsMissing;
        ProjectionTdFactor upstream(rawa,rawb,va,vb,td,td,ra,rb);
        upstream.Evaluate(params,referenceResidual,nullptr);
        correctFixedTimeObservation(fa,TR,ROW);
        correctFixedTimeObservation(fb,TR,ROW);
        ProjectionFactor corrected(fa.head<3>(),fb.head<3>());
        corrected.Evaluate(params,correctedResidual,nullptr);
        maxResidual=std::max(maxResidual,Eigen::Map<Eigen::Vector2d>(correctedResidual).norm());
        maxDifference=std::max(maxDifference,(Eigen::Map<Eigen::Vector2d>(referenceResidual)-Eigen::Map<Eigen::Vector2d>(correctedResidual)).norm());
        if(fa[4]!=ra || fb[4]!=rb || fa[5]!=va.x() || fb[6]!=vb.y())return 2;
        auto unchanged=fa;
        correctFixedTimeObservation(unchanged,0,ROW);
        if((unchanged-fa).norm()!=0)return 3;
    }
    std::cout<<"cases=250 detects_missing="<<detectsMissing<<" max_corrected_residual="<<maxResidual
             <<" max_pinned_factor_difference="<<maxDifference<<"\n";
    return detectsMissing==250 && maxResidual<1e-12 && maxDifference<1e-12 ? 0 : 1;
}
