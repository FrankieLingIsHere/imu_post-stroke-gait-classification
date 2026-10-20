#pragma once
#include <cmath>
#include <memory>
#include "cam/CamBase.h"
#include "utils/quat_ops.h"

namespace gait {
struct RowMapPoint { Eigen::Vector2f source; bool valid; };
/** Inverse image map: preserve identity, and reject noninvertible lens rays.
 * OpenCV's finite-iteration undistortion is not an exact inverse, particularly
 * near a nonmonotonic radtan edge. Reprojecting it as an absolute pixel location
 * injects a warp even when angular motion is zero. Apply only the rotation delta.
 */
inline RowMapPoint rowMapPoint(const Eigen::Vector2f& pixel,
                              const std::shared_ptr<ov_core::CamBase>& camera,
                              const Eigen::Vector3d& angular,double rowSeconds) {
  const Eigen::Vector2f normalized=camera->undistort_f(pixel);
  if(!normalized.allFinite())return {pixel,false};
  const Eigen::Vector2f zero=camera->distort_f(normalized);
  if(!zero.allFinite()||(zero-pixel).norm()>.5f)return {pixel,false};
  if(angular.squaredNorm()==0||rowSeconds==0)return {pixel,true};
  const Eigen::Vector3d ray=ov_core::exp_so3(-angular*rowSeconds)*Eigen::Vector3d(normalized.x(),normalized.y(),1);
  if(!ray.allFinite()||ray.z()<=.1)return {pixel,false};
  const Eigen::Vector2f rotated=camera->distort_f(Eigen::Vector2f(ray.x()/ray.z(),ray.y()/ray.z()));
  const Eigen::Vector2f source=pixel+(rotated-zero);
  if(!source.allFinite()||source.x()<0||source.x()>639||source.y()<0||source.y()>479)return {pixel,false};
  return {source,true};
}
}
