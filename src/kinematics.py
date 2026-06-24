"""Cinématique différentielle (base tri-cycle : 2 roues motrices + 1 roue folle).

- inverse : (v, w) demandés -> vitesses angulaires des roues gauche/droite
- forward : vitesses roues -> (v, w) réels, puis intégration de la pose (x, y, theta)
"""
import math


def inverse(v, w, track, r):
    """v: m/s (avance), w: rad/s (rotation). Renvoie (omega_gauche, omega_droite) en rad/s."""
    v_left = v - w * track / 2.0
    v_right = v + w * track / 2.0
    return v_left / r, v_right / r


def forward(omega_left, omega_right, track, r):
    """Renvoie (v, w) réels à partir des vitesses roues."""
    v_left = omega_left * r
    v_right = omega_right * r
    v = (v_left + v_right) / 2.0
    w = (v_right - v_left) / track
    return v, w


def integrate_pose(pose, v, w, dt):
    """pose = (x, y, theta). Intègre le déplacement sur dt."""
    x, y, theta = pose
    x += v * math.cos(theta) * dt
    y += v * math.sin(theta) * dt
    theta += w * dt
    # garde theta dans [-pi, pi]
    theta = (theta + math.pi) % (2 * math.pi) - math.pi
    return (x, y, theta)
