"""Pilotage interactif du robot émulé (fenêtre temps réel).

Nécessite pygame-ce :  pip install pygame-ce
Lancer :  python -m sim.interactive

Commandes :
  Flèches / ZQSD : avancer, reculer, tourner
  ESPACE         : arrêt d'urgence (bascule)
  X              : simuler une perte réseau (watchdog -> arrêt)
  R              : réinitialiser la position
  ECHAP          : quitter
"""
import math
import sys

try:
    import pygame
except ImportError:
    sys.exit("pygame manquant. Installe-le avec : pip install pygame-ce")

from src.robot import Robot
from src.config import RobotConfig

PPM = 200      # pixels par mètre
TURN_RATE = 1.5  # rad/s (vitesse de rotation au pilotage)
W, H = 900, 700


def to_screen(x, y):
    return int(W / 2 + x * PPM), int(H / 2 - y * PPM)


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("POCAA — robot émulé (pilotage)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    cfg = RobotConfig()
    robot = Robot(cfg)
    trail = []
    t = 0.0
    sim_disconnect = False  # touche X : simule une coupure réseau
    # murs invisibles : le robot ne peut pas sortir du cadre de la fenêtre
    margin = cfg.track_width / 2          # rayon du robot (m)
    x_limit = (W / 2) / PPM - margin
    y_limit = (H / 2) / PPM - margin
    running = True
    while running:
        dt = clock.tick(50) / 1000.0
        t += dt
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if e.key == pygame.K_SPACE:
                    if robot.safety.state == robot.safety.ESTOP:
                        robot.safety.clear_estop()
                    else:
                        robot.safety.trigger_estop()
                if e.key == pygame.K_x:
                    sim_disconnect = not sim_disconnect
                if e.key == pygame.K_r:
                    robot.pose = (0.0, 0.0, math.pi / 2)
                    trail.clear()

        keys = pygame.key.get_pressed()
        v = w = 0.0
        if keys[pygame.K_UP] or keys[pygame.K_z]:
            v = cfg.max_linear_speed * 0.8
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            v = -cfg.max_linear_speed * 0.3
        if keys[pygame.K_LEFT] or keys[pygame.K_q]:
            w = TURN_RATE
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            w = -TURN_RATE
        # commande envoyée À CHAQUE FRAME (0 si rien n'est pressé) :
        # le robot s'arrête net au relâché, plus de dérive.
        # Sauf si on simule une coupure réseau (touche X) -> le watchdog agit.
        if not sim_disconnect:
            robot.command(v, w, t)

        tel = robot.step(dt, t)
        # on borne la position dans le cadre (le robot glisse le long des bords)
        bx = max(-x_limit, min(x_limit, tel["x"]))
        by = max(-y_limit, min(y_limit, tel["y"]))
        robot.pose = (bx, by, robot.pose[2])
        tel["x"], tel["y"] = bx, by
        trail.append((bx, by))
        if len(trail) > 600:
            trail.pop(0)

        # rendu
        screen.fill((14, 36, 54))
        for i in range(1, len(trail)):
            pygame.draw.line(screen, (91, 84, 201), to_screen(*trail[i-1]), to_screen(*trail[i]), 2)
        x, y, th = tel["x"], tel["y"], tel["theta"]
        cx, cy = to_screen(x, y)
        color = (45, 212, 191) if tel["state"] == "NORMAL" else (239, 68, 68)
        pygame.draw.circle(screen, color, (cx, cy), int(cfg.track_width / 2 * PPM))
        hx, hy = to_screen(x + cfg.track_width * math.cos(th), y + cfg.track_width * math.sin(th))
        pygame.draw.line(screen, (255, 255, 255), (cx, cy), (hx, hy), 4)

        for i, txt in enumerate([
            f"État : {tel['state']}",
            f"v = {tel['v']:.2f} m/s   w = {tel['w']:.2f} rad/s",
            f"roue G = {tel['meas_l']:.1f}   roue D = {tel['meas_r']:.1f} rad/s",
            "Flèches/ZQSD : piloter   ESPACE : arrêt urgence   X : perte réseau   R : reset",
        ]):
            screen.blit(font.render(txt, True, (230, 236, 245)), (12, 10 + i * 24))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
