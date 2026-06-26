"""Robot émulé : assemble moteurs, encodeurs, PID, rampes, cinématique et sécurité.

C'est l'objet qu'on fait tourner dans la simulation. Il reçoit des commandes
haut niveau (v, w) — comme si elles venaient du Raspberry Pi via Websocket — et
fait l'asservissement bas niveau — comme le ferait l'ESP32.
"""
import math

from . import kinematics
from .motor import DCMotor, Encoder
from .pid import PID, Ramp
from .safety import SafetyFSM
from .config import RobotConfig

# Capteurs de proximité avant : angles (rad) relatifs au cap du robot.
SENSOR_ANGLES = [math.radians(d) for d in (-40, -20, 0, 20, 40)]


class Robot:
    def __init__(self, cfg: RobotConfig = None, world=None):
        self.cfg = cfg or RobotConfig()
        self.world = world              # monde avec obstacles (None = pas d'anticollision)
        c = self.cfg
        self.motor_l = DCMotor(c.motor_max_speed, c.motor_tau)
        self.motor_r = DCMotor(c.motor_max_speed, c.motor_tau)
        self.enc_l = Encoder(c.encoder_ticks_per_rev)
        self.enc_r = Encoder(c.encoder_ticks_per_rev)
        self.pid_l = PID(c.kp, c.ki, c.kd)
        self.pid_r = PID(c.kp, c.ki, c.kd)
        # rampe sur la vitesse roue : accélération douce, décélération plus rapide
        rate_up = c.motor_max_speed / c.accel_time
        rate_down = c.motor_max_speed / c.decel_time
        self.ramp_l = Ramp(rate_up, rate_down)
        self.ramp_r = Ramp(rate_up, rate_down)
        self.safety = SafetyFSM(c.watchdog_timeout, c.reverse_limit)

        self.pose = (0.0, 0.0, 0.0)        # x, y, theta
        self._cmd = (0.0, 0.0)             # v, w demandés
        self._last_cmd_time = 0.0

    def command(self, v, w, now):
        """Commande haut niveau (avance v en m/s, rotation w en rad/s)."""
        self._cmd = (v, w)
        self._last_cmd_time = now

    def _front_distance(self):
        """Distance au plus proche obstacle dans l'arc avant (capteurs simulés)."""
        if self.world is None:
            return float("inf")
        x, y, th = self.pose
        rng = self.cfg.sensor_range
        return min(self.world.ray_distance(x, y, th + a, rng) for a in SENSOR_ANGLES)

    def step(self, dt, now):
        """Un pas de la boucle de contrôle. Renvoie un dict de télémétrie."""
        c = self.cfg
        v, w = self._cmd

        # anticollision : on bride l'avance si un obstacle est détecté devant
        dmin = self._front_distance()
        avoid = False
        if v > 0 and dmin < c.collision_slow:
            if dmin <= c.collision_stop:
                v = 0.0
            else:
                v *= (dmin - c.collision_stop) / (c.collision_slow - c.collision_stop)
            avoid = True

        # consigne roues (cinématique inverse)
        target_l, target_r = kinematics.inverse(v, w, c.track_width, c.wheel_radius)

        # sécurité : watchdog / arrêt d'urgence -> consigne forcée à 0
        allowed = self.safety.update(now, self._last_cmd_time)
        if not allowed:
            target_l = target_r = 0.0

        # rampes d'accélération
        sp_l = self.ramp_l.update(target_l, dt)
        sp_r = self.ramp_r.update(target_r, dt)

        # mesures encodeurs (vitesse réelle des roues)
        meas_l = self.enc_l.update(self.motor_l.speed, dt)
        meas_r = self.enc_r.update(self.motor_r.speed, dt)

        # PID -> commande moteur, puis bridage marche arrière
        u_l = self.safety.clamp_reverse(self.pid_l.update(sp_l, meas_l, dt))
        u_r = self.safety.clamp_reverse(self.pid_r.update(sp_r, meas_r, dt))

        # application aux moteurs
        wl = self.motor_l.step(u_l, dt)
        wr = self.motor_r.step(u_r, dt)

        # cinématique directe + intégration de la pose
        v_real, w_real = kinematics.forward(wl, wr, c.track_width, c.wheel_radius)
        self.pose = kinematics.integrate_pose(self.pose, v_real, w_real, dt)

        return {
            "t": now, "state": self.safety.state,
            "sp_l": sp_l, "sp_r": sp_r, "meas_l": wl, "meas_r": wr,
            "u_l": u_l, "u_r": u_r,
            "x": self.pose[0], "y": self.pose[1], "theta": self.pose[2],
            "v": v_real, "w": w_real,
            "dmin": dmin, "avoid": avoid,
        }
