"""Ideal rigid-attachment IMU, in SI units; no anatomical or clinical labels."""
import numpy as np
from scipy.signal import savgol_filter
from scipy.spatial.transform import Rotation


def virtual_imu(time_s, origin_world_m, body_to_world, *, offset_body_m,
                sensor_to_body, gravity_world_m_s2, smoothing_samples=21):
    """Return trimmed times and [ax,ay,az,gx,gy,gz] in the sensor frame.

    Positions and rotations must describe one contiguous, uniformly sampled
    motion. The attachment is fixed: p_sensor=p_origin+R_body*offset.
    Accelerometer specific force is R_sensor.T*(p_sensor''-gravity).
    Gyroscope uses centered local rotation increments (radians/second).
    No noise model, missing-frame interpolation or automatic frame correction.
    """
    t, p, r = (np.asarray(x, dtype=float) for x in
               (time_s, origin_world_m, body_to_world))
    offset, attachment, gravity = (np.asarray(x, dtype=float) for x in
                                   (offset_body_m, sensor_to_body, gravity_world_m_s2))
    if (t.ndim != 1 or p.shape != (len(t), 3) or r.shape != (len(t), 3, 3)
            or offset.shape != (3,) or attachment.shape != (3, 3)
            or gravity.shape != (3,)):
        raise ValueError('Invalid time, pose or attachment shape.')
    if any(not np.isfinite(x).all() for x in (t, p, r, offset, attachment, gravity)):
        raise ValueError('All inputs must be finite; split missing-data runs first.')
    if (isinstance(smoothing_samples, bool) or not isinstance(smoothing_samples, int)
            or smoothing_samples < 5 or smoothing_samples % 2 != 1
            or len(t) <= smoothing_samples):
        raise ValueError('Smoothing requires an odd integer >=5 and a longer run.')
    dt = np.diff(t)
    if np.any(dt <= 0) or not np.allclose(dt, dt[0], rtol=1e-5, atol=1e-9):
        raise ValueError('Timestamps must be increasing and uniformly sampled.')
    for matrix in (r, attachment):
        if (not np.allclose(np.swapaxes(matrix, -1, -2) @ matrix, np.eye(3), atol=1e-6)
                or not np.allclose(np.linalg.det(matrix), 1., atol=1e-6)):
            raise ValueError('Rotations must be orthonormal and right handed.')
    position = p + np.einsum('nij,j->ni', r, offset)
    sensor = r @ attachment
    acceleration = savgol_filter(position, smoothing_samples, 3, deriv=2,
                                 delta=dt[0], axis=0)
    force = np.einsum('nji,nj->ni', sensor, acceleration - gravity)
    local = np.swapaxes(sensor[1:-1], 1, 2)
    forward = Rotation.from_matrix(local @ sensor[2:]).as_rotvec()
    backward = Rotation.from_matrix(local @ sensor[:-2]).as_rotvec()
    gyro = (forward - backward) / (2 * dt[0])
    margin = smoothing_samples // 2
    keep = slice(margin, -margin)
    signals = np.column_stack((force[keep], gyro[margin-1:len(t)-margin-1]))
    if not np.isfinite(signals).all():
        raise ValueError('Derived IMU is nonfinite.')
    return t[keep].copy(), signals
