"""Logique d'appariement du relais (sans dépendance réseau, donc testable).

Un « room » relie UN robot (le PC qui fait tourner la simulation) à
plusieurs « pilotes » (navigateurs). Le relais ne fait que router :
  - message d'un pilote  -> envoyé au robot du même room
  - message du robot     -> diffusé à tous les pilotes du même room

Les connexions sont des objets opaques (peu importe leur type) : le hub
renvoie juste la liste des destinataires, c'est l'appelant qui envoie.
"""


class Room:
    def __init__(self):
        self.robot = None      # une seule connexion robot
        self.pilots = set()    # plusieurs pilotes


class Hub:
    def __init__(self):
        self.rooms = {}

    def _room(self, name):
        return self.rooms.setdefault(name, Room())

    def add_robot(self, room, conn):
        self._room(room).robot = conn

    def add_pilot(self, room, conn):
        self._room(room).pilots.add(conn)

    def remove(self, room, conn):
        r = self.rooms.get(room)
        if not r:
            return
        if r.robot is conn:
            r.robot = None
        r.pilots.discard(conn)
        if r.robot is None and not r.pilots:
            self.rooms.pop(room, None)

    def robot_of(self, room):
        """Destinataire d'une commande venant d'un pilote (le robot, ou None)."""
        r = self.rooms.get(room)
        return r.robot if r else None

    def pilots_of(self, room):
        """Destinataires d'une télémétrie venant du robot (les pilotes)."""
        r = self.rooms.get(room)
        return list(r.pilots) if r else []

    def has_robot(self, room):
        r = self.rooms.get(room)
        return bool(r and r.robot is not None)
