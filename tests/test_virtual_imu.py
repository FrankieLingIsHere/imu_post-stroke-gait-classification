import unittest
import numpy as np
from numpy.testing import assert_allclose
from scipy.spatial.transform import Rotation
from src.data.virtual_imu import virtual_imu


class VirtualIMUTests(unittest.TestCase):
    def setUp(self):
        self.t = np.arange(501) / 100.
        self.p = np.zeros((501, 3))
        self.r = np.tile(np.eye(3), (501, 1, 1))
        self.kw = dict(offset_body_m=[0., 0., 0.], sensor_to_body=np.eye(3),
                       gravity_world_m_s2=[0., 0., -9.80665])

    def run_imu(self, p=None, r=None, **kw):
        return virtual_imu(self.t, self.p if p is None else p,
                           self.r if r is None else r, **(self.kw | kw))[1]

    def test_stationary_rotated_sensor_and_trim(self):
        q = Rotation.from_euler('x', 90, degrees=True).as_matrix()
        x = self.run_imu(sensor_to_body=q)
        self.assertEqual(x.shape, (481, 6))
        assert_allclose(x[:, :3], np.tile([0, 9.80665, 0], (481, 1)), atol=1e-10)
        assert_allclose(x[:, 3:], 0., atol=1e-10)

    def test_free_fall_zero_specific_force(self):
        p = .5 * self.t[:, None]**2 * np.array([0., 0., -9.80665])
        assert_allclose(self.run_imu(p=p), 0., atol=1e-8)

    def test_rotating_offset_has_centripetal_acceleration(self):
        r = Rotation.from_euler('z', self.t[:, None]).as_matrix()
        x = self.run_imu(r=r, offset_body_m=[.2, 0, 0])
        assert_allclose(x[:, :3], np.tile([-.2, 0., 9.80665], (481, 1)), atol=2e-4)
        assert_allclose(x[:, 3:], np.tile([0, 0, 1], (481, 1)), atol=1e-10)

    def test_global_frame_change_preserves_sensor_reading(self):
        r = Rotation.from_euler('z', self.t[:, None]).as_matrix()
        p = np.column_stack((self.t**2, self.t, self.t*0))
        q = Rotation.from_euler('xyz', [.3, -.8, .2]).as_matrix()
        x = self.run_imu(p=p, r=r, offset_body_m=[.2, 0, 0])
        y = self.run_imu(p=p @ q.T, r=q @ r, offset_body_m=[.2, 0, 0],
                         gravity_world_m_s2=q @ np.array(self.kw['gravity_world_m_s2']))
        assert_allclose(x, y, atol=1e-8)

    def test_angular_acceleration(self):
        r = Rotation.from_euler('z', .1*self.t[:, None]**2).as_matrix()
        x = self.run_imu(r=r)
        assert_allclose(x[:, 5], .2*self.t[10:-10], atol=1e-10)

    def test_rejects_gaps_nonfinite_and_invalid_rotations(self):
        for kind in ['gap', 'nan', 'reflection', 'shear']:
            t, p, r = self.t.copy(), self.p.copy(), self.r.copy()
            if kind == 'gap': t[100:] += .01
            if kind == 'nan': p[100, 0] = np.nan
            if kind == 'reflection': r[:, 0, 0] = -1
            if kind == 'shear': r[:, 0, 1] = .1
            with self.assertRaises(ValueError): virtual_imu(t, p, r, **self.kw)


if __name__ == '__main__':
    unittest.main()
