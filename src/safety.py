"""Sécurité logicielle (story S33) : machine à états + watchdog réseau.

États :
- NORMAL        : fonctionnement standard
- WATCHDOG_STOP : plus de commande reçue depuis > timeout (perte réseau) -> arrêt
- ESTOP         : arrêt d'urgence déclenché manuellement

Tant qu'on n'est pas en NORMAL, la consigne de vitesse est forcée à 0.
La marche arrière est par ailleurs bridée (reverse_limit).
"""


class SafetyFSM:
    NORMAL = "NORMAL"
    WATCHDOG_STOP = "WATCHDOG_STOP"
    ESTOP = "ESTOP"

    def __init__(self, watchdog_timeout, reverse_limit):
        self.watchdog_timeout = watchdog_timeout
        self.reverse_limit = reverse_limit
        self.state = self.NORMAL
        self._estop_latched = False

    def trigger_estop(self):
        self._estop_latched = True

    def clear_estop(self):
        self._estop_latched = False

    def update(self, now, last_command_time):
        """Met à jour l'état. Renvoie True si le mouvement est autorisé."""
        if self._estop_latched:
            self.state = self.ESTOP
        elif now - last_command_time > self.watchdog_timeout:
            self.state = self.WATCHDOG_STOP
        else:
            self.state = self.NORMAL
        return self.state == self.NORMAL

    def clamp_reverse(self, command):
        """Bride la commande moteur en marche arrière à reverse_limit."""
        if command < 0:
            return max(command, -self.reverse_limit)
        return command
