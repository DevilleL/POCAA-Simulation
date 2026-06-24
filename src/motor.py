"""Modèle simplifié d'un moteur DC + encodeur (pour tester sans matériel).

Le moteur est modélisé comme un système du premier ordre : la vitesse de la roue
tend vers (commande * vitesse_max) avec une constante de temps tau. C'est suffisant
pour développer et régler le PID avant d'avoir le vrai moteur.
"""
import math


class DCMotor:
    def __init__(self, max_speed: float, tau: float):
        self.max_speed = max_speed   # rad/s à pleine commande
        self.tau = tau               # s
        self.speed = 0.0             # rad/s (vitesse réelle de la roue)

    def step(self, command: float, dt: float) -> float:
        """command dans [-1, 1] (rapport cyclique PWM signé). Renvoie la vitesse roue."""
        command = max(-1.0, min(1.0, command))
        target = command * self.max_speed
        # réponse du 1er ordre : d(speed)/dt = (target - speed) / tau
        self.speed += (target - self.speed) / self.tau * dt
        return self.speed


class Encoder:
    """Encodeur incrémental : compte les ticks et estime la vitesse mesurée."""
    def __init__(self, ticks_per_rev: int):
        self.ticks_per_rev = ticks_per_rev
        self.angle = 0.0     # rad cumulés
        self.ticks = 0
        self._last_angle = 0.0

    def update(self, wheel_speed: float, dt: float) -> float:
        """Intègre la vitesse roue, met à jour les ticks, renvoie la vitesse mesurée."""
        self.angle += wheel_speed * dt
        self.ticks = int(self.angle / (2 * math.pi) * self.ticks_per_rev)
        measured = (self.angle - self._last_angle) / dt if dt > 0 else 0.0
        self._last_angle = self.angle
        return measured
