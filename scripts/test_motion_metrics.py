"""Regression tests for frame-boundary and cyclic footfall interpretation."""
import unittest
import numpy as np
import audit_exported_motion as audit


class ContactInterpretation(unittest.TestCase):
    def test_lateral_walk_accepts_any_cycle_origin(self):
        order=['LH','LF','RH','RF']
        for i in range(4): self.assertTrue(audit.sequence_is_lateral(order[i:]+order[:i]))

    def test_reversed_v3_walk_is_rejected(self):
        self.assertFalse(audit.sequence_is_lateral(['LH','RF','RH','LF']))
        self.assertFalse(audit.sequence_is_lateral(['LH','LF','RF']))
        self.assertFalse(audit.sequence_is_lateral(['LH','LF','RH','LH']))

    def test_contact_at_loop_boundary_is_one_landing(self):
        f=audit.FLOOR
        report=audit.contact_events([f,f,f+.05,f+.05,f])
        self.assertEqual(report['touchdown_frames'],[0])
        self.assertEqual(report['liftoff_frames'],[2])
        self.assertEqual(report['touchdown_phases'],[0.])
        self.assertEqual(report['support_fraction'],.5)

    def test_static_paw_is_not_a_gait(self):
        report=audit.contact_events([audit.FLOOR]*5)
        self.assertEqual(report['touchdown_frames'],[])
        self.assertEqual(report['liftoff_frames'],[])

    def test_contact_threshold_is_explicit(self):
        f=audit.FLOOR
        report=audit.contact_events([f+.0005,f+.0015,f+.0005])
        self.assertEqual(report['contact'],[True,False])

    def test_circular_diagonal_phase_distance(self):
        self.assertAlmostEqual(audit.circular_distance(.98,.02),.04)
        self.assertEqual(audit.circular_distance(0,.5),.5)
        self.assertEqual(audit.circular_distance(0,1),0)

    def test_source_head_exposes_sideways_neutral(self):
        self.assertAlmostEqual(audit.yaw(-audit.BACK,audit.HEAD_FORWARD),70.04851073581948)
        self.assertAlmostEqual(audit.yaw(-audit.BACK,-audit.BACK),0)

    def test_pelvis_local_measurement_removes_body_motion(self):
        yaw=.7; body=np.array([[np.cos(yaw),-np.sin(yaw),0,.4],[np.sin(yaw),np.cos(yaw),0,-.8],[0,0,1,.2],[0,0,0,1]])
        original=np.array([.8,.3,-.6])
        np.testing.assert_allclose(audit.point(np.linalg.inv(body),audit.point(body,original)),original,atol=1e-12)


if __name__=='__main__': unittest.main()
