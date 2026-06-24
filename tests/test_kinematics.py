"""Tests de la cinématique différentielle."""
import math
from src import kinematics


def test_inverse_forward_coherents():
    track, r = 0.30, 0.072
    wl, wr = kinematics.inverse(0.5, 0.8, track, r)
    v, w = kinematics.forward(wl, wr, track, r)
    assert abs(v - 0.5) < 1e-9 and abs(w - 0.8) < 1e-9


def test_ligne_droite():
    track, r = 0.30, 0.072
    wl, wr = kinematics.inverse(0.5, 0.0, track, r)
    assert abs(wl - wr) < 1e-9  # roues à la même vitesse


def test_rotation_sur_place():
    track, r = 0.30, 0.072
    wl, wr = kinematics.inverse(0.0, 1.0, track, r)
    assert wl == -wr  # roues opposées


def test_integration_pose_avance():
    pose = kinematics.integrate_pose((0, 0, 0), 1.0, 0.0, 1.0)
    assert abs(pose[0] - 1.0) < 1e-9 and abs(pose[1]) < 1e-9
