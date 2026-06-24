# POCAA — Locomotion & sécurité (simulateur)

Partie **Louis** du projet POCAA : développement et validation du code de
locomotion **sans matériel**, grâce à un robot émulé en Python.

L'idée : la logique d'asservissement (PID), la cinématique et la sécurité sont
identiques quelle que soit la cible. On les met au point ici, en simulation, puis
on les réutilise dans Webots (contrôleur Python) et enfin sur l'**ESP32**
(en C++ ou MicroPython) une fois le matériel disponible.

## Matériel visé (rappel)

- **Raspberry Pi 4** : cerveau (coordination, IA, vision) — envoie les ordres haut niveau.
- **ESP32 DevKit v1** : contrôleur moteurs — reçoit les ordres via série/USB, pilote
  les ponts en H et fait l'asservissement PID grâce aux encodeurs.
- 2 moteurs DC brushless 12 V avec encodeurs + 1 roue folle (base tri-cycle).

Le simulateur reproduit cette chaîne : commande haut niveau `(v, w)` → cinématique
inverse → rampe → **PID par roue** → modèle moteur → encodeur → cinématique directe
→ pose du robot.

## Structure

```
src/
  config.py       Paramètres (roues, moteurs, gains PID, sécurité)
  motor.py        Modèle moteur DC + encodeur
  kinematics.py   Cinématique différentielle (tri-cycle)
  pid.py          Régulateur PID + rampe d'accélération   <- cœur S32
  safety.py       Watchdog réseau, arrêt d'urgence (FSM)  <- S33
  robot.py        Assemble le tout, boucle de contrôle
sim/
  simulate.py     Scénario + graphes (PID, trajectoire) + animation GIF
  interactive.py  Pilotage en temps réel au clavier (pygame)
tests/            Tests unitaires (PID, rampes, cinématique)
outputs/          Images générées
```

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

```bash
# 1) Simulation + graphes de validation (génère outputs/*.png et robot.gif)
python -m sim.simulate

# 2) Pilotage interactif au clavier (flèches / ZQSD, ESPACE = arrêt d'urgence)
python -m sim.interactive

# 3) Tests
python -m pytest tests        # ou : python tests/test_pid.py
```

## Lien avec les tâches Jira

| Story | Couverture dans ce projet |
|-------|---------------------------|
| S31 Architecture firmware ESP32 | structure de la boucle de contrôle (`robot.py`) |
| S32 PID & rampes d'accélération | `pid.py` (PID + Ramp), validé par `sim/simulate.py` |
| S33 Sécurité (watchdog, arrêt d'urgence) | `safety.py` (FSM, bridage marche arrière) |
| S34 Protocole de pilotage | `robot.command(v, w)` = interface des messages reçus |
| S35 Simulateur 2D & tests | `sim/` + `tests/` |

## Prochaines étapes

1. Régler finement les gains PID (`config.py`) selon les courbes de `pid_tracking.png`.
2. Brancher le protocole Websocket/MQTT (S34) sur `robot.command()`.
3. Rejouer la même logique dans **Webots** (contrôleur Python) pour la démo de septembre.
4. Porter le PID sur l'**ESP32** (MicroPython ou C++) en phase matérielle.
