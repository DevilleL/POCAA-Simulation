"""Tests de l'asservissement et des rampes."""
from src.pid import PID, Ramp
from src.motor import DCMotor


def test_pid_atteint_la_consigne():
    pid = PID(0.7, 1.1, 0.0)
    motor = DCMotor(max_speed=11.0, tau=0.15)
    dt, target = 0.02, 6.0
    for _ in range(500):
        u = pid.update(target, motor.speed, dt)
        motor.step(u, dt)
    assert abs(motor.speed - target) < 0.1, motor.speed


def test_rampe_limite_la_variation():
    ramp = Ramp(max_rate=10.0)  # 10 unités/s
    v = ramp.update(100.0, 0.1)  # au plus 1.0 par pas de 0.1 s
    assert abs(v - 1.0) < 1e-9


def test_pid_sature_dans_les_bornes():
    pid = PID(5.0, 0.0, 0.0, out_min=-1.0, out_max=1.0)
    assert pid.update(100.0, 0.0, 0.02) == 1.0
    assert pid.update(-100.0, 0.0, 0.02) == -1.0
