"""Monde 2D pour l'anticollision : obstacles circulaires + lancer de rayon.

Les capteurs de proximité du robot « tirent » un rayon ; cette classe calcule
la distance au premier obstacle rencontré (intersection rayon / cercle).
"""
import math


class World:
    def __init__(self, obstacles=None):
        # obstacles : liste de (x, y, rayon) en mètres
        self.obstacles = list(obstacles or [])

    def ray_distance(self, px, py, angle, max_range):
        """Distance au premier obstacle le long du rayon partant de (px, py)
        dans la direction `angle`. Renvoie `max_range` si rien n'est touché."""
        dx, dy = math.cos(angle), math.sin(angle)
        best = max_range
        for (ox, oy, r) in self.obstacles:
            # intersection rayon (origine px,py, direction unitaire) / cercle (o, r)
            fx, fy = px - ox, py - oy
            b = 2.0 * (fx * dx + fy * dy)
            c = fx * fx + fy * fy - r * r
            disc = b * b - 4.0 * c
            if disc < 0:
                continue
            sq = math.sqrt(disc)
            t1 = (-b - sq) / 2.0
            t2 = (-b + sq) / 2.0
            # première intersection positive (devant le capteur)
            t = t1 if t1 > 0 else (t2 if t2 > 0 else None)
            if t is not None and t < best:
                best = t
        return best
