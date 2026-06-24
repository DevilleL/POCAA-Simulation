"""Tests de la session robot pilotée à distance (sans réseau)."""
from web_control.robot_client import RobotSession


def test_avance_sur_commande():
    s = RobotSession()
    s.on_command(0.5, 0.0)                     # avance
    for _ in range(100):                        # 2 s à 50 Hz
        s.on_command(0.5, 0.0)                  # on continue d'envoyer (comme le navigateur)
        tel = s.step(0.02)
    assert tel["x"] > 0.3                        # le robot a avancé
    assert tel["state"] == "NORMAL"


def test_watchdog_si_plus_de_commande():
    s = RobotSession()
    s.on_command(0.6, 0.0)
    for _ in range(20):                          # on roule un peu
        s.on_command(0.6, 0.0); s.step(0.02)
    # plus aucune commande reçue -> le watchdog doit finir par couper
    tel = None
    for _ in range(60):                          # > 0.5 s sans commande
        tel = s.step(0.02)
    assert tel["state"] == "WATCHDOG_STOP"


def test_bornage_dans_le_cadre():
    s = RobotSession()
    for _ in range(2000):                        # on fonce longtemps tout droit
        s.on_command(0.8, 0.0); s.step(0.02)
    tel = s.step(0.02)
    assert abs(tel["x"]) <= s.x_limit + 1e-6     # jamais hors du cadre
