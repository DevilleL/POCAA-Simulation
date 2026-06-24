# Pilotage de la simulation depuis le web

Permet de **piloter la simulation (qui reste sur ton PC) depuis un navigateur,
de n'importe où**, sans ouvrir de port sur ta box. C'est la story **S34**
(protocole de pilotage temps réel).

## Principe

```
[Ton PC : robot_client.py]                 [Render : relay.py]                 [Navigateur]
  exécute la simulation       --WSS sortant-->  relais public  <--WSS--  page de contrôle + vue
  applique les commandes reçues               (apparie robot/pilotes)      envoie les commandes
  diffuse la télémétrie (25 Hz)                                            dessine le robot
```

- **WebSocket** (pas REST) : temps réel bidirectionnel, faible latence.
- Le PC se **connecte en sortant** vers Render → pas de configuration routeur.
- Sécurité : un **token** partagé (`PILOT_TOKEN`) protège l'accès ; le **watchdog**
  arrête le robot si la connexion tombe.

## 1) Déployer le relais sur Render

1. Pousse ce dossier (`robot-locomotion`) sur un dépôt GitHub.
2. Sur Render : **New > Blueprint** (le fichier `render.yaml` est détecté), ou
   **New > Web Service** avec :
   - Root Directory : `robot-locomotion`
   - Build : `pip install -r web_control/requirements.txt`
   - Start : `uvicorn web_control.relay:app --host 0.0.0.0 --port $PORT`
3. Ajoute la variable d'environnement **`PILOT_TOKEN`** (choisis une valeur secrète).
4. Render te donne une URL : `https://pocaa-relay.onrender.com`.

> Astuce : le plan gratuit s'endort après inactivité → le premier accès peut
> prendre ~30 s (cold start).

## 2) Lancer le robot sur ton PC

```powershell
py -m pip install websockets
py -m web_control.robot_client --url wss://pocaa-relay.onrender.com --room demo --token TON_TOKEN
```

Le PC se connecte au relais et attend les pilotes. (Pas besoin de la fenêtre pygame :
`robot_client` exécute lui-même la simulation.)

## 3) Piloter depuis le navigateur

Ouvre simplement l'URL Render (`https://pocaa-relay.onrender.com`) sur **n'importe quel
appareil**, saisis le même **room** et **token**, clique **Se connecter**, puis pilote :

- Clavier : flèches ou ZQSD.
- Mobile : boutons tactiles à l'écran.
- Bouton **STOP** : arrêt immédiat.

Tu vois le robot bouger en temps réel (canvas) avec sa télémétrie.

## Tester en local (sans Render)

```powershell
py -m pip install -r web_control/requirements.txt
# terminal 1 — le relais
py -m uvicorn web_control.relay:app --port 8000
# terminal 2 — le robot
py -m web_control.robot_client --url ws://localhost:8000 --room demo --token demo-token-change-me
# navigateur : http://localhost:8000  (room=demo, token=demo-token-change-me)
```

## Sécurité — à ne pas oublier

- **Change `PILOT_TOKEN`** (la valeur par défaut est publique).
- Le token est visible côté navigateur : suffisant pour une démo, mais pour un usage
  réel, prévoir une vraie authentification (login) côté relais.
- Le watchdog (0,5 s) reste la sécurité ultime : si le réseau tombe, le robot s'arrête.
