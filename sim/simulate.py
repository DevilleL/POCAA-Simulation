"""Simulation headless : joue un scénario et génère des graphes de validation.

Lance :  python -m sim.simulate
Produit dans outputs/ :
  - pid_tracking.png : consigne vs vitesse réelle des roues (qualité de l'asservissement)
  - trajectory.png   : trajectoire vue de dessus
  - robot.gif        : animation du déplacement
Le scénario inclut une accélération, un virage, puis une perte réseau (watchdog).
"""
import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import imageio.v2 as imageio

from src.robot import Robot
from src.config import RobotConfig

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs")
os.makedirs(OUT, exist_ok=True)


def scenario(t):
    """Renvoie (v, w, envoyer_commande) à l'instant t.
    De 7 s à 8 s on coupe l'envoi de commandes pour simuler une perte réseau."""
    if t < 3.0:
        return 0.6, 0.0, True          # ligne droite, accélération
    elif t < 5.0:
        return 0.4, 1.2, True          # virage à gauche
    elif t < 7.0:
        return 0.6, 0.0, True          # ligne droite
    elif t < 8.0:
        return 0.6, 0.0, False         # perte réseau -> watchdog
    else:
        return 0.3, -1.0, True         # reprise, virage à droite


def run():
    cfg = RobotConfig()
    robot = Robot(cfg)
    dt = cfg.control_dt
    T = 11.0
    log = []
    t = 0.0
    while t < T:
        v, w, send = scenario(t)
        if send:
            robot.command(v, w, t)
        log.append(robot.step(dt, t))
        t += dt

    ts = np.array([d["t"] for d in log])
    return cfg, log, ts


def plot_pid(cfg, log, ts):
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for ax, side, name in zip(axes, ("l", "r"), ("gauche", "droite")):
        ax.plot(ts, [d[f"sp_{side}"] for d in log], "--", color="#FBBF24", lw=2, label="consigne (rampe)")
        ax.plot(ts, [d[f"meas_{side}"] for d in log], color="#11897A", lw=1.8, label="vitesse réelle (encodeur)")
        ax.set_ylabel(f"Roue {name}\n(rad/s)")
        ax.grid(alpha=0.3)
        ax.legend(loc="upper right", fontsize=8)
    # zone watchdog (7-8 s)
    for ax in axes:
        ax.axvspan(7.0, 8.0, color="#EF4444", alpha=0.12)
    axes[0].set_title("Asservissement PID — suivi consigne / vitesse réelle\n(zone rouge = perte réseau, watchdog -> arrêt)")
    axes[1].set_xlabel("temps (s)")
    fig.tight_layout()
    p = os.path.join(OUT, "pid_tracking.png")
    fig.savefig(p, dpi=110)
    plt.close(fig)
    return p


def plot_trajectory(cfg, log):
    xs = [d["x"] for d in log]
    ys = [d["y"] for d in log]
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(xs, ys, color="#5B54C9", lw=2)
    ax.plot(xs[0], ys[0], "o", color="#11897A", ms=10, label="départ")
    ax.plot(xs[-1], ys[-1], "s", color="#EF4444", ms=10, label="arrivée")
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    ax.set_title("Trajectoire du robot (vue de dessus)")
    ax.legend()
    fig.tight_layout()
    p = os.path.join(OUT, "trajectory.png")
    fig.savefig(p, dpi=110)
    plt.close(fig)
    return p


def make_gif(cfg, log):
    xs = [d["x"] for d in log]; ys = [d["y"] for d in log]
    th = [d["theta"] for d in log]
    L = cfg.track_width
    margin = 0.5
    xmin, xmax = min(xs) - margin, max(xs) + margin
    ymin, ymax = min(ys) - margin, max(ys) + margin
    frames = []
    step = 5  # 1 image toutes les 5 itérations (10 fps)
    for i in range(0, len(log), step):
        fig, ax = plt.subplots(figsize=(5, 5))
        ax.plot(xs[:i+1], ys[:i+1], color="#5B54C9", lw=1.5, alpha=0.8)
        x, y, t = xs[i], ys[i], th[i]
        # corps du robot
        ax.add_patch(plt.Circle((x, y), L/2, color="#13334E", alpha=0.9))
        # direction
        ax.plot([x, x + (L/1.5)*math.cos(t)], [y, y + (L/1.5)*math.sin(t)], color="#2DD4BF", lw=3)
        ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)
        ax.set_aspect("equal"); ax.grid(alpha=0.25)
        ax.set_title(f"t = {log[i]['t']:.1f} s   état: {log[i]['state']}", fontsize=10)
        fig.tight_layout()
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (4,))
        frames.append(frame[:, :, :3].copy())
        plt.close(fig)
    p = os.path.join(OUT, "robot.gif")
    imageio.mimsave(p, frames, fps=10, loop=0)
    return p


if __name__ == "__main__":
    cfg, log, ts = run()
    print("Vitesse linéaire max théorique : %.2f m/s" % cfg.max_linear_speed)
    print("PID :", plot_pid(cfg, log, ts))
    print("Trajectoire :", plot_trajectory(cfg, log))
    print("Animation :", make_gif(cfg, log))
    print("Pose finale : x=%.2f y=%.2f theta=%.1f°" % (log[-1]["x"], log[-1]["y"], math.degrees(log[-1]["theta"])))
