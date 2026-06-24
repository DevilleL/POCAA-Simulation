"""Régulateur PID + rampe d'accélération.

C'est LE cœur de la story S32. Le PID asservit la vitesse de chaque roue :
il compare la consigne (vitesse voulue) à la mesure (encodeur) et calcule la
commande moteur. La rampe limite la variation de consigne pour éviter les à-coups.
"""


class PID:
    def __init__(self, kp, ki, kd, out_min=-1.0, out_max=1.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.out_min, self.out_max = out_min, out_max
        self._integral = 0.0
        self._prev_error = 0.0

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0

    def update(self, setpoint, measurement, dt):
        error = setpoint - measurement
        # terme intégral avec anti-emballement (anti-windup)
        self._integral += error * dt
        derivative = (error - self._prev_error) / dt if dt > 0 else 0.0
        output = self.kp * error + self.ki * self._integral + self.kd * derivative
        # saturation de la sortie + anti-windup (on retient l'intégrale si saturé)
        if output > self.out_max:
            output = self.out_max
            self._integral -= error * dt
        elif output < self.out_min:
            output = self.out_min
            self._integral -= error * dt
        self._prev_error = error
        return output


class Ramp:
    """Limite la vitesse de variation d'une consigne.

    On peut donner une décélération plus rapide que l'accélération
    (freinage réaliste + meilleure précision au pilotage).
    """
    def __init__(self, max_rate, max_rate_down=None):
        self.max_rate = max_rate                                   # unité/s (accélération)
        self.max_rate_down = max_rate_down if max_rate_down is not None else max_rate
        self.value = 0.0

    def update(self, target, dt):
        # on "décélère" quand on se rapproche de zéro (|consigne| < |valeur|)
        rate = self.max_rate_down if abs(target) < abs(self.value) else self.max_rate
        max_step = rate * dt
        delta = target - self.value
        if delta > max_step:
            delta = max_step
        elif delta < -max_step:
            delta = -max_step
        self.value += delta
        return self.value
