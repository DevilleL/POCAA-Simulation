"""Tests du routage du relais (sans réseau)."""
from web_control.hub import Hub


def test_appariement_et_routage():
    hub = Hub()
    robot = object(); p1 = object(); p2 = object()
    hub.add_robot("r", robot)
    hub.add_pilot("r", p1)
    hub.add_pilot("r", p2)
    assert hub.has_robot("r")
    assert hub.robot_of("r") is robot                 # commande pilote -> robot
    assert set(hub.pilots_of("r")) == {p1, p2}        # télémétrie robot -> pilotes


def test_isolation_des_rooms():
    hub = Hub()
    ra, rb = object(), object()
    hub.add_robot("a", ra); hub.add_robot("b", rb)
    pa = object(); hub.add_pilot("a", pa)
    assert hub.pilots_of("b") == []
    assert hub.robot_of("a") is ra and hub.robot_of("b") is rb


def test_nettoyage_a_la_deconnexion():
    hub = Hub()
    robot = object(); p = object()
    hub.add_robot("r", robot); hub.add_pilot("r", p)
    hub.remove("r", p)
    assert hub.pilots_of("r") == []
    hub.remove("r", robot)
    assert "r" not in hub.rooms          # room vide -> supprimée
